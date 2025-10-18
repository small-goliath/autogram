"""Repository for admin operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import Admin
from api.repositories.base_repository import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    """Repository for admin operations."""

    def __init__(self):
        super().__init__(Admin)

    async def get_by_username(
        self,
        db: AsyncSession,
        username: str
    ) -> Optional[Admin]:
        """Get admin by username."""
        result = await db.execute(
            select(Admin).where(Admin.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[Admin]:
        """Get admin by email."""
        result = await db.execute(
            select(Admin).where(Admin.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_admins(self, db: AsyncSession) -> List[Admin]:
        """Get all active admins."""
        result = await db.execute(
            select(Admin).where(Admin.is_active == True)
        )
        return list(result.scalars().all())

    async def get_superadmins(self, db: AsyncSession) -> List[Admin]:
        """Get all superadmins."""
        result = await db.execute(
            select(Admin).where(Admin.is_superadmin == True)
        )
        return list(result.scalars().all())

    async def update_last_login(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Admin]:
        """Update last login timestamp."""
        admin = await self.get_by_id(db, id)
        if not admin:
            return None

        admin.last_login_at = datetime.utcnow()
        await db.flush()
        await db.refresh(admin)
        return admin
