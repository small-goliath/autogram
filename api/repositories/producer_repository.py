"""Repository for producer operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import Producer
from api.repositories.base_repository import BaseRepository


class ProducerRepository(BaseRepository[Producer]):
    """Repository for producer operations."""

    def __init__(self):
        super().__init__(Producer)

    async def get_by_instagram_id(
        self,
        db: AsyncSession,
        instagram_id: str
    ) -> Optional[Producer]:
        """Get producer by Instagram ID."""
        result = await db.execute(
            select(Producer).where(Producer.instagram_id == instagram_id)
        )
        return result.scalar_one_or_none()

    async def get_active_producers(self, db: AsyncSession) -> List[Producer]:
        """Get all active and verified producers."""
        result = await db.execute(
            select(Producer).where(
                Producer.is_active == True,
                Producer.is_verified == True
            )
        )
        return list(result.scalars().all())

    async def get_unverified_producers(self, db: AsyncSession) -> List[Producer]:
        """Get all unverified producers."""
        result = await db.execute(
            select(Producer).where(Producer.is_verified == False)
        )
        return list(result.scalars().all())

    async def verify_producer(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Producer]:
        """Mark producer as verified."""
        producer = await self.get_by_id(db, id)
        if not producer:
            return None

        producer.is_verified = True
        await db.flush()
        await db.refresh(producer)
        return producer

    async def update_last_used(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[Producer]:
        """Update last used timestamp."""
        producer = await self.get_by_id(db, id)
        if not producer:
            return None

        producer.last_used_at = datetime.utcnow()
        await db.flush()
        await db.refresh(producer)
        return producer

    async def update_session(
        self,
        db: AsyncSession,
        id: int,
        session_data: str
    ) -> Optional[Producer]:
        """Update producer session data."""
        producer = await self.get_by_id(db, id)
        if not producer:
            return None

        producer.session_data = session_data
        await db.flush()
        await db.refresh(producer)
        return producer
