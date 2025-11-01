"""
user_action_verification 테이블의 링크를 확인하고 댓글 작성자가 있으면 삭제하는 배치
"""
import os
import sys
from typing import Optional
import instaloader
import asyncio
import random

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select, delete
from core.database import get_session_maker
from core.models import UserActionVerification, VerificationRetryQueue
from core.instagram_helper import get_instaloader_with_helper
from core.utils import get_kst_now
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end
from batch.utils.discord_notifier import DiscordNotifier


logger = setup_logger("cleanup_verifications")


def extract_shortcode_from_url(url: str) -> Optional[str]:
    """
    Instagram URL에서 shortcode를 추출합니다.

    Args:
        url: Instagram URL

    Returns:
        shortcode 또는 None
    """
    import re
    pattern = r'instagram\.com/(?:p|reel)/([^/?]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


async def get_post_interactions(
    loader: instaloader.Instaloader,
    shortcode: str,
    helper_username: str = "unknown"
) -> tuple[set[str], set[str], str | None, bool]:
    """
    포스트의 댓글 작성자와 좋아요 누른 사람 username 목록을 가져옵니다.

    Args:
        loader: Instaloader 인스턴스
        shortcode: Instagram 포스트 shortcode
        helper_username: Helper 계정 username (로깅용)

    Returns:
        (댓글 작성자 username 집합, 좋아요 누른 사람 username 집합, 에러 메시지 또는 None, 재시도 가능 여부)
    """
    try:
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # 댓글 작성자 수집
        commenters = set()
        for comment in post.get_comments():
            commenters.add(comment.owner.username.lower())

        # 좋아요 누른 사람 수집
        likers = set()
        for liker in post.get_likes():
            likers.add(liker.username.lower())

        logger.debug(
            f"  📝 {shortcode}: 댓글 {len(commenters)}명, "
            f"좋아요 {len(likers)}명"
        )

        # 성공 시 랜덤 딜레이 (5-10초, feedback_required 방지)
        await asyncio.sleep(random.uniform(5, 10))
        return commenters, likers, None, False

    except Exception as e:
        error_msg = str(e)

        # Critical 에러: Helper 계정이 차단됨 - 배치 즉시 중단 필요
        CRITICAL_ERRORS = [
            "feedback_required",
            "challenge_required",
            "checkpoint_required",
            "consent_required",
            "spam"
        ]

        if any(critical_err in error_msg.lower() for critical_err in CRITICAL_ERRORS):
            logger.critical(f"🚨 Helper 계정 차단 감지 (@{helper_username}, {shortcode}): {error_msg[:200]}")
            logger.critical("⚠️ 배치를 즉시 중단합니다. Helper 계정 상태를 확인해주세요.")
            # 배치 중단을 위해 예외 발생
            raise Exception(f"Helper account blocked: @{helper_username} - {error_msg}")

        # 접근 불가 포스트는 재시도 불가
        SKIP_ERRORS = [
            "not found",
            "deleted",
            "private",
            "comments disabled",
            "unavailable"
        ]

        if any(skip_err in error_msg.lower() for skip_err in SKIP_ERRORS):
            logger.info(f"ℹ️ 접근 불가 포스트 ({shortcode}): {error_msg[:100]}")
            await asyncio.sleep(random.uniform(1, 2))
            return set(), set(), error_msg, False

        # Rate limit 또는 일시적 오류는 재시도 가능
        is_retryable = (
            "something went wrong" in error_msg.lower() or
            "429" in error_msg or
            "fail" in error_msg.lower()
        )

        if is_retryable:
            logger.warning(f"⚠️ Rate limit 감지 ({shortcode}) - 재시도 큐에 저장")
        else:
            logger.error(f"❌ 포스트 조회 실패 ({shortcode}): {error_msg[:150]}")

        await asyncio.sleep(random.uniform(5, 10))
        return set(), set(), error_msg, is_retryable


async def cleanup_verifications() -> dict:
    """
    user_action_verification 테이블을 확인하고 댓글을 작성한 사용자는 삭제합니다.

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # 1. 모든 검증 레코드 조회
            result = await session.execute(
                select(
                    UserActionVerification.id,
                    UserActionVerification.username,
                    UserActionVerification.instagram_link,
                    UserActionVerification.link_owner_username
                )
            )
            verifications = result.fetchall()
            logger.info(f"📊 검증 레코드: {len(verifications)}개")

            if not verifications:
                logger.info("✅ 확인할 검증 레코드가 없습니다.")
                return {"총 검증": 0, "삭제됨": 0, "유지됨": 0}

            # 2. Instagram Helper 로드
            loader, helper = await get_instaloader_with_helper(session)

            if not loader:
                logger.error("❌ 사용 가능한 Helper 계정이 없습니다.")
                raise Exception("Helper 계정 없음")

            logger.info(f"🔑 Helper 계정: {helper.instagram_username}")

            # 3. 링크별로 그룹화 (같은 링크는 한 번만 조회)
            links_to_check = {}  # {instagram_link: [(id, username), ...]}
            for vid, username, link, _owner in verifications:
                if link not in links_to_check:
                    links_to_check[link] = []
                links_to_check[link].append((vid, username))

            logger.info(f"🔗 확인할 고유 링크: {len(links_to_check)}개")

            # 4. 각 링크의 댓글 확인 및 삭제 처리
            deleted_count = 0
            maintained_count = 0
            failed_posts = []  # 포스트 조회 실패 건 수집

            for instagram_link, verification_list in links_to_check.items():
                shortcode = extract_shortcode_from_url(instagram_link)

                if not shortcode:
                    logger.warning(f"⚠️ Shortcode 추출 실패: {instagram_link}")
                    maintained_count += len(verification_list)
                    continue

                logger.info(f"🔍 확인 중: {shortcode}")

                # 댓글 작성자와 좋아요 누른 사람 조회
                commenters, likers, error_msg, is_retryable = await get_post_interactions(
                    loader, shortcode, helper.instagram_username
                )

                # 포스트 조회 실패 시 처리
                if error_msg:
                    # Rate limit 등 재시도 가능한 오류는 큐에 저장
                    if is_retryable:
                        # 중복 확인
                        existing = await session.execute(
                            select(VerificationRetryQueue).where(
                                VerificationRetryQueue.shortcode == shortcode,
                                VerificationRetryQueue.batch_type == "cleanup",
                                VerificationRetryQueue.status.in_(["pending", "processing"])
                            )
                        )
                        if not existing.scalar_one_or_none():
                            retry_item = VerificationRetryQueue(
                                instagram_link=instagram_link,
                                shortcode=shortcode,
                                batch_type="cleanup",
                                link_owner_username=None,  # cleanup은 link_owner가 없음
                                last_error_message=error_msg[:500],
                                last_attempt_at=get_kst_now(),
                                status="pending"
                            )
                            session.add(retry_item)
                            await session.commit()
                            logger.info(f"  📥 재시도 큐에 저장: {shortcode}")
                    else:
                        # 재시도 불가능한 오류는 그냥 기록
                        failed_posts.append({
                            "shortcode": shortcode,
                            "link": instagram_link,
                            "error": error_msg,
                            "affected_users": len(verification_list)
                        })
                    maintained_count += len(verification_list)  # 실패한 경우 모두 유지
                    continue

                logger.debug(
                    f"  📝 댓글 {len(commenters)}명, 좋아요 {len(likers)}명"
                )

                # 댓글 또는 좋아요 한 사람 (둘 중 하나라도 함)
                interacted_users = commenters | likers

                # 각 검증 레코드 확인
                for verification_id, username in verification_list:
                    # 댓글 또는 좋아요를 했으면 삭제
                    if username.lower() in interacted_users:
                        await session.execute(
                            delete(UserActionVerification).where(
                                UserActionVerification.id == verification_id
                            )
                        )
                        deleted_count += 1
                        logger.debug(f"  ✅ 삭제: {username} (참여 확인)")
                    else:
                        maintained_count += 1
                        logger.debug(f"  ⏸️ 유지: {username} (미참여)")

                await session.commit()

            logger.info(f"📊 정리 완료: {deleted_count}개 삭제, {maintained_count}개 유지")

            if failed_posts:
                logger.warning(f"⚠️ 포스트 조회 실패: {len(failed_posts)}개")
                for failed in failed_posts:
                    logger.warning(f"  - {failed['shortcode']} (영향받는 사용자: {failed['affected_users']}명)")

            result = {
                "총 검증": len(verifications),
                "삭제됨": deleted_count,
                "유지됨": maintained_count,
            }

            # 실패 건이 있으면 결과에 포함
            if failed_posts:
                result["포스트 조회 실패"] = len(failed_posts)
                result["실패 상세"] = "\n".join([
                    f"• {f['shortcode']} (영향: {f['affected_users']}명): {f['error'][:150]}"
                    for f in failed_posts
                ])

            return result
        except Exception:
            await session.rollback()
            raise


async def main():
    """메인 실행 함수"""
    log_batch_start(logger, "검증 레코드 정리 배치")

    notifier = DiscordNotifier()
    success = False
    details = {}
    error_message = None

    try:
        details = await cleanup_verifications()
        success = True

    except Exception as e:
        error_str = str(e)
        logger.error(f"❌ 배치 실행 중 오류 발생: {error_str}", exc_info=True)

        # Helper account blocked 에러인 경우 특별 처리
        if "Helper account blocked" in error_str:
            error_message = f"⚠️ Helper 계정 차단됨 - {error_str}"
            details = {"오류": "Helper 계정 차단", "상세": error_str}
        else:
            error_message = error_str
            details = {"오류": error_str}

    finally:
        log_batch_end(logger, "검증 레코드 정리 배치", success)

        # Discord 알림
        notifier.send_batch_result(
            batch_name="검증 레코드 정리",
            success=success,
            details=details,
            error_message=error_message
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
