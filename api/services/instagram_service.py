"""Instagram service for Instagram API operations."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.instagram_helper import InstagramHelper, InstagramCommentBot
from core.schemas import UnfollowCheckerRequest, UnfollowCheckerResponse
from core.security import decrypt_password
from api.repositories.helper_repository import HelperRepository


class InstagramService:
    """Service for Instagram operations."""

    def __init__(self):
        self.helper_repo = HelperRepository()
        self.instagram_helper = InstagramHelper()
        self.comment_bot = InstagramCommentBot()

    async def get_post_comments(
        self,
        db: AsyncSession,
        post_url: str
    ) -> List[dict]:
        """
        Get all comments from an Instagram post using a helper account.

        Args:
            db: Database session
            post_url: Instagram post URL

        Returns:
            List of comments with username and text
        """
        # Get least used helper
        helper = await self.helper_repo.get_least_used_helper(db)
        if not helper:
            raise HTTPException(status_code=503, detail="No helper accounts available")

        # Extract shortcode from URL
        shortcode = self.instagram_helper.extract_shortcode_from_url(post_url)
        if not shortcode:
            raise HTTPException(status_code=400, detail="Invalid Instagram URL")

        try:
            # Login with session
            if helper.session_data:
                success = self.instagram_helper.login_with_session(
                    helper.instagram_id,
                    helper.session_data
                )
                if not success:
                    raise Exception("Failed to login with session")

            # Get comments
            comments = self.instagram_helper.get_post_comments(shortcode)

            # Update helper last used
            await self.helper_repo.update_last_used(db, helper.id)

            return comments

        except Exception as e:
            # Increment login attempts on failure
            await self.helper_repo.increment_login_attempts(db, helper.id)
            raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

    async def check_if_user_commented(
        self,
        db: AsyncSession,
        post_url: str,
        username: str
    ) -> bool:
        """
        Check if a specific user commented on a post.

        Args:
            db: Database session
            post_url: Instagram post URL
            username: Instagram username to check

        Returns:
            True if user commented, False otherwise
        """
        comments = await self.get_post_comments(db, post_url)

        # Check if username is in comments
        for comment in comments:
            if comment['username'].lower() == username.lower():
                return True

        return False

    async def post_comment(
        self,
        db: AsyncSession,
        post_url: str,
        comment_text: str,
        producer_id: int
    ) -> bool:
        """
        Post a comment on an Instagram post using a producer account.

        Args:
            db: Database session
            post_url: Instagram post URL
            comment_text: Comment text to post
            producer_id: ID of producer account to use

        Returns:
            True if successful
        """
        from api.repositories.producer_repository import ProducerRepository

        producer_repo = ProducerRepository()
        producer = await producer_repo.get_by_id(db, producer_id)

        if not producer:
            raise HTTPException(status_code=404, detail="Producer not found")

        if not producer.is_active or not producer.is_verified:
            raise HTTPException(status_code=400, detail="Producer is not active or verified")

        try:
            # Login with session or password
            if producer.session_data:
                success = self.comment_bot.login_with_session(
                    producer.instagram_id,
                    producer.session_data
                )
            else:
                success, session_data = self.comment_bot.login_with_password(
                    producer.instagram_id,
                    producer.instagram_password_encrypted,
                    producer.verification_code
                )
                if success and session_data:
                    await producer_repo.update_session(db, producer_id, session_data)

            if not success:
                raise Exception("Failed to login to Instagram")

            # Post comment
            result = self.comment_bot.post_comment(post_url, comment_text)

            # Update last used
            await producer_repo.update_last_used(db, producer_id)

            return result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to post comment: {str(e)}")

    async def check_unfollowers(
        self,
        db: AsyncSession,
        data: UnfollowCheckerRequest
    ) -> UnfollowCheckerResponse:
        """
        Check unfollowers for a user's Instagram account.

        Args:
            db: Database session
            data: Request with Instagram credentials

        Returns:
            List of unfollowers
        """
        try:
            # Login to Instagram
            success, session_data = self.comment_bot.login_with_password(
                data.instagram_id,
                data.instagram_password,
                data.verification_code
            )

            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to login to Instagram. Please check credentials."
                )

            # Get unfollowers
            unfollowers = self.comment_bot.get_unfollowers(data.instagram_id)

            return UnfollowCheckerResponse(
                unfollowers=unfollowers,
                count=len(unfollowers)
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to check unfollowers: {str(e)}"
            )
