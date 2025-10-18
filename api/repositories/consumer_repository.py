"""Repository for consumer operations."""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import Consumer
from api.repositories.base_repository import BaseRepository


class ConsumerRepository(BaseRepository[Consumer]):
    """Repository for consumer operations."""

    def __init__(self):
        super().__init__(Consumer)

    async def get_by_instagram_id(
        self,
        db: AsyncSession,
        instagram_id: str
    ) -> Optional[Consumer]:
        """Get consumer by Instagram ID."""
        result = await db.execute(
            select(Consumer).where(Consumer.instagram_id == instagram_id)
        )
        return result.scalar_one_or_none()

    async def get_active_consumers(self, db: AsyncSession) -> List[Consumer]:
        """Get all active consumers."""
        result = await db.execute(
            select(Consumer).where(Consumer.is_active == True)
        )
        return list(result.scalars().all())

    async def deactivate(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Consumer]:
        """Deactivate a consumer."""
        consumer = await self.get_by_id(db, id)
        if not consumer:
            return None

        consumer.is_active = False
        await db.flush()
        await db.refresh(consumer)
        return consumer
