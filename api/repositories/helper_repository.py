"""Repository for helper account operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import Helper
from api.repositories.base_repository import BaseRepository


class HelperRepository(BaseRepository[Helper]):
    """Repository for helper account operations."""

    def __init__(self):
        super().__init__(Helper)

    async def get_by_instagram_id(
        self,
        db: AsyncSession,
        instagram_id: str
    ) -> Optional[Helper]:
        """Get helper by Instagram ID."""
        result = await db.execute(
            select(Helper).where(Helper.instagram_id == instagram_id)
        )
        return result.scalar_one_or_none()

    async def get_active_helpers(self, db: AsyncSession) -> List[Helper]:
        """Get all active helpers."""
        result = await db.execute(
            select(Helper).where(
                Helper.is_active == True,
                Helper.is_locked == False
            )
        )
        return list(result.scalars().all())

    async def get_least_used_helper(self, db: AsyncSession) -> Optional[Helper]:
        """Get the least recently used active helper."""
        result = await db.execute(
            select(Helper)
            .where(
                Helper.is_active == True,
                Helper.is_locked == False
            )
            .order_by(Helper.last_used_at.asc().nullsfirst())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_last_used(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Helper]:
        """Update last used timestamp."""
        helper = await self.get_by_id(db, id)
        if not helper:
            return None

        helper.last_used_at = datetime.utcnow()
        await db.flush()
        await db.refresh(helper)
        return helper

    async def increment_login_attempts(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Helper]:
        """Increment login attempts counter."""
        helper = await self.get_by_id(db, id)
        if not helper:
            return None

        helper.login_attempts += 1

        # Lock account after 3 failed attempts
        if helper.login_attempts >= 3:
            helper.is_locked = True

        await db.flush()
        await db.refresh(helper)
        return helper

    async def reset_login_attempts(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Helper]:
        """Reset login attempts counter."""
        helper = await self.get_by_id(db, id)
        if not helper:
            return None

        helper.login_attempts = 0
        helper.is_locked = False
        await db.flush()
        await db.refresh(helper)
        return helper

    async def update_session(
        self,
        db: AsyncSession,
        id: int,
        session_data: str
    ) -> Optional[Helper]:
        """Update helper session data."""
        helper = await self.get_by_id(db, id)
        if not helper:
            return None

        helper.session_data = session_data
        await db.flush()
        await db.refresh(helper)
        return helper
