"""Repository for notice operations."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import Notice
from api.repositories.base_repository import BaseRepository


class NoticeRepository(BaseRepository[Notice]):
    """Repository for notice operations."""

    def __init__(self):
        super().__init__(Notice)

    async def get_pinned_notices(self, db: AsyncSession) -> List[Notice]:
        """Get all pinned notices."""
        result = await db.execute(
            select(Notice)
            .where(Notice.is_pinned == True)
            .order_by(Notice.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_important_notices(self, db: AsyncSession) -> List[Notice]:
        """Get all important notices."""
        result = await db.execute(
            select(Notice)
            .where(Notice.is_important == True)
            .order_by(Notice.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_recent_notices(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[Notice]:
        """Get recent notices."""
        result = await db.execute(
            select(Notice)
            .order_by(Notice.is_pinned.desc(), Notice.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_view_count(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Notice]:
        """Increment view count."""
        notice = await self.get_by_id(db, id)
        if not notice:
            return None

        notice.view_count += 1
        await db.flush()
        await db.refresh(notice)
        return notice
