"""
user_action_verification 테이블의 레코드를 재검증하는 배치
댓글/좋아요를 하지 않았던 사용자가 이후에 참여했는지 확인하고 레코드 정리
"""
import os
import sys
from typing import Optional
import asyncio
import random

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select, delete
from core.database import get_session_maker
from core.models import UserActionVerification
from core.instagram_helper import get_instaloader_with_helper
from core.comment_downloader import CommentDownloader
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end


logger = setup_logger("cleanup_verifications")


def extract_shortcode_from_url(url: str) -> Optional[str]:
    """Instagram URL에서 shortcode를 추출합니다."""
    import re
    pattern = r'instagram\.com/(?:p|reel)/([^/?]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


async def cleanup_verifications() -> dict:
    """
    user_action_verification 테이블의 레코드를 재검증합니다.
    댓글/좋아요를 했으면 레코드 삭제, 안 했으면 유지

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            # 1. 모든 검증 레코드 조회
            result = await session.execute(
                select(UserActionVerification)
            )
            verifications = result.scalars().all()
            logger.info(f"📊 재검증 대상: {len(verifications)}개 레코드")

            if not verifications:
                logger.warning("⚠️ 재검증할 레코드가 없습니다.")
                return {"총 레코드 수": 0, "삭제됨": 0, "유지됨": 0}

            # 2. link_owner별로 그룹화 (bulk 다운로드를 위해)
            owner_to_verifications = {}
            for v in verifications:
                if v.link_owner_username not in owner_to_verifications:
                    owner_to_verifications[v.link_owner_username] = []
                owner_to_verifications[v.link_owner_username].append(v)

            logger.info(f"📝 고유 link_owner 수: {len(owner_to_verifications)}명")

            # 3. Instagram Helper 로드
            loader, helper = await get_instaloader_with_helper(session)

            if not loader:
                logger.error("❌ 사용 가능한 Helper 계정이 없습니다.")
                raise Exception("Helper 계정 없음")

            logger.info(f"🔑 Helper 계정: {helper.instagram_username}")

            # 4. CommentDownloader 인스턴스 생성
            downloader = CommentDownloader(loader, helper.instagram_username)

            # 5. 각 link_owner별로 재검증
            deleted_count = 0
            kept_count = 0
            failed_downloads = []

            for link_owner, owner_verifications in owner_to_verifications.items():
                logger.info(f"📥 재검증 중: @{link_owner} ({len(owner_verifications)}개 레코드)")

                try:
                    # 최근 30일 포스트 다운로드
                    posts_data, error = downloader.download_user_posts_bulk(
                        link_owner, days_back=30
                    )

                    if error:
                        error_lower = error.lower()

                        # Critical 에러 체크
                        CRITICAL_ERRORS = [
                            "feedback_required", "challenge_required",
                            "checkpoint_required", "consent_required",
                            "spam", "login required"
                        ]

                        if any(critical_err in error_lower for critical_err in CRITICAL_ERRORS):
                            logger.critical(f"🚨 Helper 계정 차단 감지 (@{helper.instagram_username}): {error[:200]}")
                            raise Exception(f"Helper account blocked: @{helper.instagram_username} - {error}")

                        logger.warning(f"⚠️ @{link_owner} 다운로드 실패: {error[:150]}")
                        failed_downloads.append({'owner': link_owner, 'error': error})
                        kept_count += len(owner_verifications)
                        continue

                    # 각 검증 레코드에 대해 확인
                    for verification in owner_verifications:
                        shortcode = extract_shortcode_from_url(verification.instagram_link)

                        if not shortcode:
                            logger.warning(f"⚠️ shortcode 추출 실패, 유지: {verification.instagram_link}")
                            kept_count += 1
                            continue

                        # 해당 shortcode의 포스트 데이터 확인
                        if shortcode not in posts_data:
                            # 포스트가 30일 범위 밖이거나 삭제됨 - 레코드 유지
                            kept_count += 1
                            logger.debug(f"  ⏩ {verification.username}: 포스트 없음, 유지")
                            continue

                        post_data = posts_data[shortcode]
                        commenters = post_data['commenters']
                        likers = post_data['likers']

                        # 사용자가 댓글 또는 좋아요를 했는지 확인
                        user_lower = verification.username.lower()
                        if user_lower in commenters or user_lower in likers:
                            # 참여했으므로 레코드 삭제
                            await session.delete(verification)
                            deleted_count += 1
                            logger.debug(f"  ✅ {verification.username}: 참여 확인, 삭제")
                        else:
                            # 여전히 참여 안 함 - 레코드 유지
                            kept_count += 1
                            logger.debug(f"  ❌ {verification.username}: 미참여, 유지")

                    await asyncio.sleep(random.uniform(5, 10))

                except Exception as e:
                    if "Helper account blocked" in str(e):
                        raise
                    logger.error(f"❌ @{link_owner} 재검증 중 예외: {str(e)[:200]}")
                    failed_downloads.append({'owner': link_owner, 'error': str(e)})
                    kept_count += len(owner_verifications)

            await session.commit()

            logger.info(f"✅ 재검증 완료: {deleted_count}개 삭제, {kept_count}개 유지")

            if failed_downloads:
                logger.warning(f"⚠️ 다운로드 실패: {len(failed_downloads)}개 link_owner")
                for fail in failed_downloads[:5]:
                    logger.warning(f"  - {fail['owner']}: {fail['error'][:100]}")

            return {
                "총 레코드 수": len(verifications),
                "삭제됨": deleted_count,
                "유지됨": kept_count,
                "다운로드 실패": len(failed_downloads)
            }

        except Exception as e:
            logger.error(f"❌ 배치 실행 중 오류 발생: {str(e)}")
            await session.rollback()
            raise


async def main():
    """배치 메인 함수"""
    log_batch_start(logger, "검증 레코드 정리")

    try:
        details = await cleanup_verifications()
        log_batch_end(logger, "성공 검증 레코드 정리")
        logger.info(f"✅ 배치 완료: {details}")

    except Exception as e:
        error_str = str(e)
        log_batch_end(logger, "실패 검증 레코드 정리")
        logger.error(f"❌ 배치 실패: {error_str}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
