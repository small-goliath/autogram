"""Action updater batch job."""
import os
import sys
import asyncio
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from core.models import UserActionVerification, SnsRaiseUser, Helper
from core.instagram_helper import InstagramHelper
from sqlalchemy import select, delete

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_actions():
    """Update user action verifications by checking if comments were posted."""
    logger.info("=" * 50)
    logger.info("Action Updater Batch Job Started")
    logger.info("=" * 50)

    async with AsyncSessionLocal() as db:
        try:
            # Get all unverified actions
            result = await db.execute(
                select(UserActionVerification).where(
                    UserActionVerification.is_commented == False
                )
            )
            unverified_actions = result.scalars().all()
            logger.info(f"Found {len(unverified_actions)} unverified actions")

            if not unverified_actions:
                logger.info("No unverified actions to check")
                return

            # Get helper account
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

            updated_count = 0
            deleted_count = 0

            # Check each unverified action
            for action in unverified_actions:
                # Get user's Instagram ID
                result = await db.execute(
                    select(SnsRaiseUser).where(SnsRaiseUser.id == action.user_id)
                )
                user = result.scalar_one_or_none()

                if not user or not user.instagram_id:
                    continue

                logger.info(
                    f"Checking if {user.username} commented on "
                    f"{action.link_owner_username}'s post"
                )

                # Get comments from Instagram
                shortcode = instagram.extract_shortcode_from_url(action.instagram_link)
                if not shortcode:
                    logger.warning(f"Invalid Instagram URL: {action.instagram_link}")
                    continue

                try:
                    comments = instagram.get_post_comments(shortcode)
                    comment_usernames = set(c['username'].lower() for c in comments)

                    # Check if user commented
                    has_commented = user.instagram_id.lower() in comment_usernames

                    if has_commented:
                        # Delete verification record (user has now commented)
                        await db.execute(
                            delete(UserActionVerification).where(
                                UserActionVerification.id == action.id
                            )
                        )
                        deleted_count += 1
                        logger.info(
                            f"✓ {user.username} has now commented! Removed from verification."
                        )
                    else:
                        logger.info(f"✗ {user.username} still hasn't commented")

                except Exception as e:
                    logger.error(f"Error checking post {action.instagram_link}: {e}")
                    continue

                # Small delay to avoid rate limiting
                await asyncio.sleep(2)

            # Update helper last used
            helper.last_used_at = datetime.now()

            await db.commit()
            logger.info(f"Deleted {deleted_count} verification records (comments found)")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error in action updater: {e}")
            raise

    logger.info("=" * 50)
    logger.info("Action Updater Batch Job Completed")
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(update_actions())
