"""Verification service for user action verification."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import UserActionVerificationCreate, UserActionVerificationResponse
from api.repositories.verification_repository import VerificationRepository


class VerificationService:
    """Service for user action verification operations."""

    def __init__(self):
        self.repo = VerificationRepository()

    async def get_all_verifications(
        self,
        db: AsyncSession,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserActionVerificationResponse]:
        """Get all verifications with optional username filter."""
        verifications = await self.repo.get_by_username_filter(db, username, skip, limit)
        return [UserActionVerificationResponse.model_validate(v) for v in verifications]

    async def get_verification_by_id(
        self,
        db: AsyncSession,
        verification_id: int
    ) -> UserActionVerificationResponse:
        """Get verification by ID."""
        verification = await self.repo.get_by_id(db, verification_id)
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        return UserActionVerificationResponse.model_validate(verification)

    async def create_verification(
        self,
        db: AsyncSession,
        data: UserActionVerificationCreate
    ) -> UserActionVerificationResponse:
        """Create a new verification record."""
        from api.repositories.sns_user_repository import SnsUserRepository
        from api.repositories.request_repository import RequestRepository

        # Verify user exists
        user_repo = SnsUserRepository()
        user = await user_repo.get_by_id(db, data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Verify request exists
        request_repo = RequestRepository()
        request = await request_repo.get_by_id(db, data.request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")

        # Check if verification already exists
        existing = await self.repo.get_by_user_and_request(
            db,
            data.user_id,
            data.request_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Verification already exists for this user and request"
            )

        # Create verification
        verification = await self.repo.create(
            db,
            user_id=data.user_id,
            request_id=data.request_id,
            instagram_link=data.instagram_link,
            link_owner_username=data.link_owner_username,
            is_commented=data.is_commented
        )

        return UserActionVerificationResponse.model_validate(verification)

    async def get_unverified_actions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserActionVerificationResponse]:
        """Get all unverified actions (users who haven't commented)."""
        verifications = await self.repo.get_unverified_actions(db, skip, limit)
        return [UserActionVerificationResponse.model_validate(v) for v in verifications]

    async def mark_as_commented(
        self,
        db: AsyncSession,
        verification_id: int
    ) -> UserActionVerificationResponse:
        """Mark verification as commented."""
        verification = await self.repo.mark_as_commented(db, verification_id)
        if not verification:
            raise HTTPException(status_code=404, detail="Verification not found")
        return UserActionVerificationResponse.model_validate(verification)

    async def delete_verification(
        self,
        db: AsyncSession,
        user_id: int,
        request_id: int
    ) -> dict:
        """Delete verification when comment is found."""
        success = await self.repo.delete_by_user_and_request(db, user_id, request_id)

        if not success:
            raise HTTPException(status_code=404, detail="Verification not found")

        return {"message": "Verification deleted successfully", "success": True}

    async def get_verifications_by_link_owner(
        self,
        db: AsyncSession,
        link_owner_username: str
    ) -> List[UserActionVerificationResponse]:
        """Get all verifications for a specific link owner."""
        verifications = await self.repo.get_by_link_owner(db, link_owner_username)
        return [UserActionVerificationResponse.model_validate(v) for v in verifications]
