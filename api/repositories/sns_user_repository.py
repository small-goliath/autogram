"""Repository for SNS raise user operations."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.models import SnsRaiseUser, RequestByWeek, UserActionVerification
from api.repositories.base_repository import BaseRepository


class SnsUserRepository(BaseRepository[SnsRaiseUser]):
    """Repository for SNS raise user operations."""

    def __init__(self):
        super().__init__(SnsRaiseUser)

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[SnsRaiseUser]:
        """Get user by username."""
        result = await db.execute(
            select(SnsRaiseUser).where(SnsRaiseUser.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_instagram_id(self, db: AsyncSession, instagram_id: str) -> Optional[SnsRaiseUser]:
        """Get user by Instagram ID."""
        result = await db.execute(
            select(SnsRaiseUser).where(SnsRaiseUser.instagram_id == instagram_id)
        )
        return result.scalar_one_or_none()

    async def get_active_users(self, db: AsyncSession) -> List[SnsRaiseUser]:
        """Get all active users."""
        result = await db.execute(
            select(SnsRaiseUser).where(SnsRaiseUser.is_active == True)
        )
        return list(result.scalars().all())

    async def delete_with_cascade(self, db: AsyncSession, id: int) -> bool:
        """Delete user and all related data (cascade)."""
        user = await self.get_by_id(db, id)
        if not user:
            return False

        # Delete related request_by_week records
        await db.execute(
            delete(RequestByWeek).where(RequestByWeek.user_id == id)
        )

        # Delete related user_action_verification records
        await db.execute(
            delete(UserActionVerification).where(UserActionVerification.user_id == id)
        )

        # Delete the user
        await db.delete(user)
        await db.flush()
        return True

    async def search_by_username(self, db: AsyncSession, query: str, limit: int = 20) -> List[SnsRaiseUser]:
        """Search users by username (partial match)."""
        result = await db.execute(
            select(SnsRaiseUser)
            .where(SnsRaiseUser.username.ilike(f"%{query}%"))
            .limit(limit)
        )
        return list(result.scalars().all())
