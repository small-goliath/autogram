"""SNS user service for user management."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import SnsRaiseUserCreate, SnsRaiseUserUpdate, SnsRaiseUserResponse
from api.repositories.sns_user_repository import SnsUserRepository


class SnsUserService:
    """Service for SNS user operations."""

    def __init__(self):
        self.repo = SnsUserRepository()

    async def get_all_users(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[SnsRaiseUserResponse]:
        """Get all users with pagination."""
        users = await self.repo.get_all(db, skip, limit)
        return [SnsRaiseUserResponse.model_validate(u) for u in users]

    async def get_user_by_id(
        self,
        db: AsyncSession,
        user_id: int
    ) -> SnsRaiseUserResponse:
        """Get user by ID."""
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return SnsRaiseUserResponse.model_validate(user)

    async def get_user_by_username(
        self,
        db: AsyncSession,
        username: str
    ) -> Optional[SnsRaiseUserResponse]:
        """Get user by username."""
        user = await self.repo.get_by_username(db, username)
        if not user:
            return None
        return SnsRaiseUserResponse.model_validate(user)

    async def create_user(
        self,
        db: AsyncSession,
        data: SnsRaiseUserCreate
    ) -> SnsRaiseUserResponse:
        """Create a new user."""
        # Check if username already exists
        existing = await self.repo.get_by_username(db, data.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Check if Instagram ID already exists
        if data.instagram_id:
            existing_ig = await self.repo.get_by_instagram_id(db, data.instagram_id)
            if existing_ig:
                raise HTTPException(status_code=400, detail="Instagram ID already exists")

        user = await self.repo.create(
            db,
            username=data.username,
            instagram_id=data.instagram_id,
            email=data.email,
            is_active=data.is_active
        )

        return SnsRaiseUserResponse.model_validate(user)

    async def update_user(
        self,
        db: AsyncSession,
        user_id: int,
        data: SnsRaiseUserUpdate
    ) -> SnsRaiseUserResponse:
        """Update a user."""
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check username uniqueness if changing
        if data.username and data.username != user.username:
            existing = await self.repo.get_by_username(db, data.username)
            if existing:
                raise HTTPException(status_code=400, detail="Username already exists")

        # Check Instagram ID uniqueness if changing
        if data.instagram_id and data.instagram_id != user.instagram_id:
            existing_ig = await self.repo.get_by_instagram_id(db, data.instagram_id)
            if existing_ig:
                raise HTTPException(status_code=400, detail="Instagram ID already exists")

        updated_user = await self.repo.update(
            db,
            user_id,
            username=data.username,
            instagram_id=data.instagram_id,
            email=data.email,
            is_active=data.is_active
        )

        return SnsRaiseUserResponse.model_validate(updated_user)

    async def delete_user(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """Delete a user with cascade (all related data)."""
        user = await self.repo.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        success = await self.repo.delete_with_cascade(db, user_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user")

        return {"message": "User deleted successfully", "success": True}

    async def get_active_users(self, db: AsyncSession) -> List[SnsRaiseUserResponse]:
        """Get all active users."""
        users = await self.repo.get_active_users(db)
        return [SnsRaiseUserResponse.model_validate(u) for u in users]

    async def search_users(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 20
    ) -> List[SnsRaiseUserResponse]:
        """Search users by username."""
        users = await self.repo.search_by_username(db, query, limit)
        return [SnsRaiseUserResponse.model_validate(u) for u in users]
