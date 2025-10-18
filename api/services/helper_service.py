"""Helper service for Instagram helper account management."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import HelperCreate, HelperResponse
from core.security import encrypt_password
from core.instagram_helper import InstagramHelper
from api.repositories.helper_repository import HelperRepository


class HelperService:
    """Service for helper account operations."""

    def __init__(self):
        self.repo = HelperRepository()
        self.instagram = InstagramHelper()

    async def get_all_helpers(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[HelperResponse]:
        """Get all helper accounts."""
        helpers = await self.repo.get_all(db, skip, limit)
        return [HelperResponse.model_validate(h) for h in helpers]

    async def get_helper_by_id(
        self,
        db: AsyncSession,
        helper_id: int
    ) -> HelperResponse:
        """Get helper by ID."""
        helper = await self.repo.get_by_id(db, helper_id)
        if not helper:
            raise HTTPException(status_code=404, detail="Helper not found")
        return HelperResponse.model_validate(helper)

    async def create_helper(
        self,
        db: AsyncSession,
        data: HelperCreate
    ) -> HelperResponse:
        """
        Create a new helper account.
        Login to Instagram and save session.
        """
        # Check if Instagram ID already exists
        existing = await self.repo.get_by_instagram_id(db, data.instagram_id)
        if existing:
            raise HTTPException(status_code=400, detail="Instagram ID already registered as helper")

        # Attempt Instagram login
        try:
            success, session_data = self.instagram.login_with_password(
                data.instagram_id,
                data.instagram_password
            )

            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to login to Instagram. Please check credentials."
                )

            # Encrypt password
            encrypted_password = encrypt_password(data.instagram_password)

            # Create helper record
            helper = await self.repo.create(
                db,
                instagram_id=data.instagram_id,
                instagram_password_encrypted=encrypted_password,
                session_data=session_data.decode() if session_data else None,
                is_active=True
            )

            return HelperResponse.model_validate(helper)

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create helper: {str(e)}"
            )

    async def delete_helper(
        self,
        db: AsyncSession,
        helper_id: int
    ) -> dict:
        """Delete a helper account."""
        helper = await self.repo.get_by_id(db, helper_id)
        if not helper:
            raise HTTPException(status_code=404, detail="Helper not found")

        success = await self.repo.delete(db, helper_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete helper")

        return {"message": "Helper deleted successfully", "success": True}

    async def get_active_helpers(self, db: AsyncSession) -> List[HelperResponse]:
        """Get all active helpers."""
        helpers = await self.repo.get_active_helpers(db)
        return [HelperResponse.model_validate(h) for h in helpers]

    async def get_least_used_helper(self, db: AsyncSession) -> Optional[HelperResponse]:
        """Get the least recently used helper for load balancing."""
        helper = await self.repo.get_least_used_helper(db)
        if not helper:
            return None
        return HelperResponse.model_validate(helper)

    async def mark_helper_used(
        self,
        db: AsyncSession,
        helper_id: int
    ) -> HelperResponse:
        """Mark helper as used (update last_used_at)."""
        helper = await self.repo.update_last_used(db, helper_id)
        if not helper:
            raise HTTPException(status_code=404, detail="Helper not found")
        return HelperResponse.model_validate(helper)
