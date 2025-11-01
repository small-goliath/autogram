"""
재시도 큐에 있는 실패한 포스트 조회를 재처리하는 배치
"""
import os
import sys
import instaloader
import asyncio
import random

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select, delete
from core.database import get_session_maker
from core.models import (
    VerificationRetryQueue,
    UserActionVerification,
    SnsRaiseUser
)
from core.instagram_helper import get_instaloader_with_helper
from core.utils import get_kst_now
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end
from batch.utils.discord_notifier import DiscordNotifier


logger = setup_logger("retry_failed_verifications")

# 최대 재시도 횟수
MAX_RETRY_COUNT = 5


async def get_post_interactions(
    loader: instaloader.Instaloader,
    shortcode: str,
    helper_username: str = "unknown"
) -> tuple[set[str], set[str], str | None]:
    """
    포스트의 댓글 작성자와 좋아요 누른 사람 username 목록을 가져옵니다.

    Args:
        loader: Instaloader 인스턴스
        shortcode: Instagram 포스트 shortcode
        helper_username: Helper 계정 username (로깅용)

    Returns:
        (댓글 작성자 username 집합, 좋아요 누른 사람 username 집합, 에러 메시지 또는 None)
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
        return commenters, likers, None

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

        logger.error(f"❌ 포스트 조회 실패 ({shortcode}): {error_msg[:150]}")
        await asyncio.sleep(random.uniform(5, 10))
        return set(), set(), error_msg


async def process_verify_type(
    session,
    retry_item: VerificationRetryQueue,
    commenters: set[str],
    likers: set[str]
) -> int:
    """
    verify 타입 재시도 항목 처리 (댓글/좋아요 미참여자 검증)

    Args:
        session: Database session
        retry_item: 재시도 큐 항목
        commenters: 댓글 작성자 username 집합
        likers: 좋아요 누른 사람 username 집합

    Returns:
        추가된 검증 레코드 수
    """
    # 모든 사용자 조회
    result = await session.execute(select(SnsRaiseUser.username))
    all_users = {row[0] for row in result.fetchall()}

    # 본인을 제외한 다른 사용자들
    other_users = all_users - {retry_item.link_owner_username}

    # 댓글 또는 좋아요 한 사람 (둘 중 하나라도 함)
    interacted_users = commenters | likers

    # 댓글도 좋아요도 안 한 사용자 찾기
    non_interacted_users = other_users - interacted_users

    # user_action_verification에 저장
    added_count = 0
    for non_interacted_user in non_interacted_users:
        # 중복 체크
        existing = await session.execute(
            select(UserActionVerification).where(
                UserActionVerification.username == non_interacted_user,
                UserActionVerification.instagram_link == retry_item.instagram_link,
                UserActionVerification.link_owner_username == retry_item.link_owner_username
            )
        )

        if existing.scalar_one_or_none():
            logger.debug(f"  ⏭️ 중복: {non_interacted_user}")
            continue

        # 새로운 검증 레코드 추가
        verification = UserActionVerification(
            username=non_interacted_user,
            instagram_link=retry_item.instagram_link,
            link_owner_username=retry_item.link_owner_username
        )
        session.add(verification)
        added_count += 1
        logger.debug(f"  ➕ 추가: {non_interacted_user} (미참여)")

    await session.commit()
    return added_count


async def process_cleanup_type(
    session,
    retry_item: VerificationRetryQueue,
    commenters: set[str],
    likers: set[str]
) -> int:
    """
    cleanup 타입 재시도 항목 처리 (댓글/좋아요 참여한 사용자 삭제)

    Args:
        session: Database session
        retry_item: 재시도 큐 항목
        commenters: 댓글 작성자 username 집합
        likers: 좋아요 누른 사람 username 집합

    Returns:
        삭제된 검증 레코드 수
    """
    # 해당 링크에 대한 모든 검증 레코드 조회
    result = await session.execute(
        select(
            UserActionVerification.id,
            UserActionVerification.username
        ).where(
            UserActionVerification.instagram_link == retry_item.instagram_link
        )
    )
    verifications = result.fetchall()

    # 댓글 또는 좋아요 한 사람 (둘 중 하나라도 함)
    interacted_users = commenters | likers

    # 댓글 또는 좋아요를 한 사용자는 삭제
    deleted_count = 0
    for verification_id, username in verifications:
        if username.lower() in interacted_users:
            await session.execute(
                delete(UserActionVerification).where(
                    UserActionVerification.id == verification_id
                )
            )
            deleted_count += 1
            logger.debug(f"  ✅ 삭제: {username} (참여 확인)")

    await session.commit()
    return deleted_count


async def retry_failed_verifications() -> dict:
    """
    재시도 큐에 있는 항목들을 처리합니다.

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # 1. pending 상태의 재시도 항목 조회
            result = await session.execute(
                select(VerificationRetryQueue)
                .where(VerificationRetryQueue.status == "pending")
                .order_by(VerificationRetryQueue.created_at.asc())
                .limit(50)  # 한 번에 최대 50개만 처리
            )
            retry_items = list(result.scalars().all())

            logger.info(f"📊 재시도 대기 항목: {len(retry_items)}개")

            if not retry_items:
                logger.info("✅ 재시도할 항목이 없습니다.")
                return {
                    "총 항목": 0,
                    "성공": 0,
                    "실패": 0,
                    "최대 재시도 초과": 0
                }

            # 2. Instagram Helper 로드
            loader, helper = await get_instaloader_with_helper(session)

            if not loader:
                logger.error("❌ 사용 가능한 Helper 계정이 없습니다.")
                raise Exception("Helper 계정 없음")

            logger.info(f"🔑 Helper 계정: {helper.instagram_username}")

            # 3. 각 항목 처리
            success_count = 0
            failed_count = 0
            max_retry_exceeded = 0

            for retry_item in retry_items:
                logger.info(f"🔄 재시도: {retry_item.shortcode} (시도 {retry_item.retry_count + 1}회)")

                # Status를 processing으로 변경
                retry_item.status = "processing"
                retry_item.last_attempt_at = get_kst_now()
                await session.commit()

                # 댓글 작성자와 좋아요 누른 사람 조회
                commenters, likers, error_msg = await get_post_interactions(
                    loader, retry_item.shortcode, helper.instagram_username
                )

                if error_msg:
                    # 실패
                    retry_item.retry_count += 1
                    retry_item.last_error_message = error_msg[:500]

                    if retry_item.retry_count >= MAX_RETRY_COUNT:
                        # 최대 재시도 횟수 초과
                        retry_item.status = "failed"
                        max_retry_exceeded += 1
                        logger.warning(
                            f"  ⛔ 최대 재시도 횟수 초과: {retry_item.shortcode} "
                            f"({retry_item.retry_count}회)"
                        )
                    else:
                        # 다시 pending으로 변경
                        retry_item.status = "pending"
                        failed_count += 1
                        logger.warning(
                            f"  ❌ 재시도 실패: {retry_item.shortcode} "
                            f"({retry_item.retry_count}/{MAX_RETRY_COUNT})"
                        )

                    await session.commit()
                    continue

                # 성공 - 타입별 처리
                if retry_item.batch_type == "verify":
                    added = await process_verify_type(session, retry_item, commenters, likers)
                    logger.info(f"  ✅ verify 처리 완료: {added}개 추가")
                elif retry_item.batch_type == "cleanup":
                    deleted = await process_cleanup_type(session, retry_item, commenters, likers)
                    logger.info(f"  ✅ cleanup 처리 완료: {deleted}개 삭제")
                else:
                    logger.warning(f"  ⚠️ 알 수 없는 batch_type: {retry_item.batch_type}")

                # 큐 항목을 completed로 변경
                retry_item.status = "completed"
                await session.commit()
                success_count += 1

            logger.info(
                f"📊 재시도 완료: {success_count}개 성공, "
                f"{failed_count}개 실패, {max_retry_exceeded}개 최대 재시도 초과"
            )

            return {
                "총 항목": len(retry_items),
                "성공": success_count,
                "실패": failed_count,
                "최대 재시도 초과": max_retry_exceeded
            }

        except Exception:
            await session.rollback()
            raise


async def main():
    """메인 실행 함수"""
    log_batch_start(logger, "재시도 큐 처리 배치")

    notifier = DiscordNotifier()
    success = False
    details = {}
    error_message = None

    try:
        details = await retry_failed_verifications()
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
        log_batch_end(logger, "재시도 큐 처리 배치", success)

        # Discord 알림
        notifier.send_batch_result(
            batch_name="재시도 큐 처리",
            success=success,
            details=details,
            error_message=error_message
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
