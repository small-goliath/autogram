"""
전송된 링크에 대해 댓글 작성 여부를 확인하고 user_action_verification 테이블에 저장하는 배치
link_owner 기준으로 bulk 다운로드하여 효율성 향상
"""
import os
import sys
from typing import Optional
import asyncio
import random

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sqlalchemy import select
from core.database import get_session_maker
from core.models import RequestByWeek, UserActionVerification, SnsRaiseUser, VerificationRetryQueue
from core.instagram_helper import get_instaloader_with_helper
from core.comment_downloader import CommentDownloader
from core.utils import get_kst_now
from batch.utils.date_helper import get_week_start_date
from batch.utils.logger import setup_logger, log_batch_start, log_batch_end
from batch.utils.discord_notifier import DiscordNotifier


logger = setup_logger("verify_comments")


def extract_shortcode_from_url(url: str) -> Optional[str]:
    """Instagram URL에서 shortcode를 추출합니다."""
    import re
    pattern = r'instagram\.com/(?:p|reel)/([^/?]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


async def verify_comments_for_week() -> dict:
    """
    이번 주 request_by_week의 모든 링크에 대해 댓글 작성 여부를 확인합니다.
    link_owner별로 bulk 다운로드하여 효율성 향상

    Returns:
        결과 통계 딕셔너리
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            week_start = get_week_start_date()

            # 1. 이번 주 요청 링크 조회
            result = await session.execute(
                select(RequestByWeek.username, RequestByWeek.instagram_link).where(
                    RequestByWeek.week_start_date == week_start
                )
            )
            requests = result.fetchall()
            logger.info(f"📊 이번 주 요청 링크: {len(requests)}개")

            if not requests:
                logger.warning("⚠️ 확인할 요청이 없습니다.")
                return {"총 링크 수": 0, "확인 완료": 0, "저장된 검증": 0}

            # 2. shortcode와 link_owner 매핑
            shortcode_to_owner = {}
            link_owners = set()

            for link_owner, instagram_link in requests:
                shortcode = extract_shortcode_from_url(instagram_link)
                if not shortcode:
                    logger.warning(f"⚠️ shortcode 추출 실패, 스킵: {instagram_link}")
                    continue

                shortcode_to_owner[shortcode] = {
                    'owner': link_owner,
                    'link': instagram_link
                }
                link_owners.add(link_owner)

            logger.info(f"📝 고유 link_owner 수: {len(link_owners)}명")
            logger.info(f"🔗 유효한 shortcode: {len(shortcode_to_owner)}개")

            # 3. 모든 사용자 목록 조회
            result = await session.execute(
                select(SnsRaiseUser.username)
            )
            all_users = {row[0] for row in result.fetchall()}
            logger.info(f"👥 전체 사용자 수: {len(all_users)}")

            # 4. Instagram Helper 로드
            loader, helper = await get_instaloader_with_helper(session)

            if not loader:
                logger.error("❌ 사용 가능한 Helper 계정이 없습니다.")
                raise Exception("Helper 계정 없음")

            logger.info(f"🔑 Helper 계정: {helper.instagram_username}")

            # 5. CommentDownloader 인스턴스 생성
            downloader = CommentDownloader(loader, helper.instagram_username)

            # 6. 각 link_owner별로 bulk 다운로드
            # 최근 22일 포스트 조회
            days_back = 22
            logger.info(f"📅 조회 기간: 최근 {days_back}일")

            all_posts_data = {}  # {shortcode: {'commenters': set, 'likers': set}}
            failed_downloads = []

            for link_owner in link_owners:
                logger.info(f"📥 다운로드 중: @{link_owner}의 최근 {days_back}일 포스트")

                try:
                    posts_data, error = downloader.download_user_posts_bulk(
                        link_owner, days_back=days_back
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
                        continue

                    # 필요한 shortcode만 필터링
                    logger.info(f"  📦 Downloaded {len(posts_data)} posts from @{link_owner}")

                    matched_count = 0
                    for shortcode, data in posts_data.items():
                        if shortcode in shortcode_to_owner:
                            all_posts_data[shortcode] = data
                            matched_count += 1
                            logger.debug(f"  ✓ Matched: {shortcode} (댓글 {len(data['commenters'])}명)")

                    if matched_count > 0:
                        logger.info(f"  ✅ {matched_count}개 포스트 매칭됨")

                    await asyncio.sleep(random.uniform(5, 10))

                except Exception as e:
                    if "Helper account blocked" in str(e):
                        raise
                    logger.error(f"❌ @{link_owner} 다운로드 중 예외: {str(e)[:200]}")
                    failed_downloads.append({'owner': link_owner, 'error': str(e)})

            logger.info(f"✅ 다운로드 완료: {len(all_posts_data)}/{len(shortcode_to_owner)}개 포스트")

            # 7. 검증 처리
            total_verifications_added = 0

            for shortcode, post_data in all_posts_data.items():
                link_info = shortcode_to_owner[shortcode]
                link_owner = link_info['owner']
                instagram_link = link_info['link']

                commenters = post_data['commenters']
                likers = post_data['likers']

                # 본인을 제외한 다른 사용자들
                other_users = all_users - {link_owner}

                # 댓글 또는 좋아요 한 사람 (둘 중 하나라도 함)
                interacted_users = commenters | likers

                # 댓글도 좋아요도 안 한 사용자 찾기
                non_interacted_users = other_users - interacted_users

                # user_action_verification에 저장
                for non_interacted_user in non_interacted_users:
                    # 중복 체크
                    existing = await session.execute(
                        select(UserActionVerification).where(
                            UserActionVerification.username == non_interacted_user,
                            UserActionVerification.instagram_link == instagram_link
                        )
                    )
                    if not existing.scalar_one_or_none():
                        new_verification = UserActionVerification(
                            username=non_interacted_user,
                            instagram_link=instagram_link,
                            link_owner_username=link_owner,
                            created_at=get_kst_now()
                        )
                        session.add(new_verification)
                        total_verifications_added += 1

            await session.commit()

            logger.info(f"📊 검증 완료: {len(all_posts_data)}개 링크, {total_verifications_added}개 검증 추가")

            if failed_downloads:
                logger.warning(f"⚠️ 다운로드 실패: {len(failed_downloads)}개 link_owner")
                for fail in failed_downloads[:5]:
                    logger.warning(f"  - {fail['owner']}: {fail['error'][:100]}")

            return {
                "총 링크 수": len(shortcode_to_owner),
                "확인 완료": len(all_posts_data),
                "저장된 검증": total_verifications_added,
                "다운로드 실패": len(failed_downloads)
            }

        except Exception as e:
            logger.error(f"❌ 배치 실행 중 오류 발생: {str(e)}")
            await session.rollback()
            raise


async def main():
    """배치 메인 함수"""
    log_batch_start(logger, "좋아요 및 댓글 작성 검증")

    try:
        details = await verify_comments_for_week()
        log_batch_end(logger, "성공 댓글 작성 검증")
        logger.info(f"✅ 배치 완료: {details}")

    except Exception as e:
        error_str = str(e)
        log_batch_end(logger, "실패 댓글 작성 검증")
        logger.error(f"❌ 배치 실패: {error_str}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
