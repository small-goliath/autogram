"""Comment verifier batch job."""
import os
import sys
import asyncio
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from core.models import RequestByWeek, SnsRaiseUser, UserActionVerification, Helper
from core.instagram_helper import InstagramHelper
from sqlalchemy import select

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_current_week_dates() -> tuple[datetime, datetime]:
    """Get current week start and end dates."""
    today = datetime.now()
    days_since_monday = today.weekday()
    week_start = today - timedelta(days=days_since_monday)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return week_start, week_end


async def verify_comments():
    """Verify comments for all requests in current week."""
    logger.info("=" * 50)
    logger.info("Comment Verifier Batch Job Started")
    logger.info("=" * 50)

    week_start, week_end = get_current_week_dates()
    logger.info(f"Checking week: {week_start.date()} to {week_end.date()}")

    async with AsyncSessionLocal() as db:
        try:
            # Get all requests for current week
            result = await db.execute(
                select(RequestByWeek).where(
                    RequestByWeek.week_start_date == week_start
                )
            )
            requests = result.scalars().all()
            logger.info(f"Found {len(requests)} requests to verify")

            # Get all active users
            result = await db.execute(
                select(SnsRaiseUser).where(SnsRaiseUser.is_active == True)
            )
            all_users = result.scalars().all()
            logger.info(f"Found {len(all_users)} active users")

            # Get helper account for Instagram API
            result = await db.execute(
                select(Helper).where(
                    Helper.is_active == True,
                    Helper.is_locked == False
                ).order_by(Helper.last_used_at.asc().nullsfirst()).limit(1)
            )
            helper = result.scalar_one_or_none()

            if not helper:
                logger.error("No active helper account available")
                return

            instagram = InstagramHelper()

            # Login with helper account
            if helper.session_data:
                success = instagram.login_with_session(
                    helper.instagram_id,
                    helper.session_data
                )
                if not success:
                    logger.error("Failed to login with helper account")
                    return

            verification_count = 0

            # For each request, check which users haven't commented
            for request in requests:
                # Get request owner
                result = await db.execute(
                    select(SnsRaiseUser).where(SnsRaiseUser.id == request.user_id)
                )
                request_owner = result.scalar_one()

                logger.info(f"Checking request from {request_owner.username}")

                # Get comments from Instagram
                shortcode = instagram.extract_shortcode_from_url(request.instagram_link)
                if not shortcode:
                    logger.warning(f"Invalid Instagram URL: {request.instagram_link}")
                    continue

                try:
                    comments = instagram.get_post_comments(shortcode)
                    comment_usernames = set(c['username'].lower() for c in comments)
                    logger.info(f"Found {len(comments)} comments on post")

                    # Check each user (except request owner)
                    for user in all_users:
                        if user.id == request.user_id:
                            continue  # Skip request owner

                        if not user.instagram_id:
                            continue  # Skip users without Instagram ID

                        # Check if user commented
                        has_commented = user.instagram_id.lower() in comment_usernames

                        if not has_commented:
                            # Check if verification already exists
                            result = await db.execute(
                                select(UserActionVerification).where(
                                    UserActionVerification.user_id == user.id,
                                    UserActionVerification.request_id == request.id
                                )
                            )
                            existing = result.scalar_one_or_none()

                            if not existing:
                                # Create verification record
                                verification = UserActionVerification(
                                    user_id=user.id,
                                    request_id=request.id,
                                    instagram_link=request.instagram_link,
                                    link_owner_username=request_owner.username,
                                    is_commented=False
                                )
                                db.add(verification)
                                verification_count += 1
                                logger.info(
                                    f"User {user.username} has not commented on "
                                    f"{request_owner.username}'s post"
                                )

                except Exception as e:
                    logger.error(f"Error checking post {request.instagram_link}: {e}")
                    continue

                # Small delay to avoid rate limiting
                await asyncio.sleep(2)

            # Update helper last used
            helper.last_used_at = datetime.now()

            await db.commit()
            logger.info(f"Created {verification_count} verification records")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error in comment verifier: {e}")
            raise

    logger.info("=" * 50)
    logger.info("Comment Verifier Batch Job Completed")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(verify_comments())
