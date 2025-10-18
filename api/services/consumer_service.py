"""Consumer service for AI comment receiver management."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import ConsumerCreate, ConsumerResponse
from api.repositories.consumer_repository import ConsumerRepository


class ConsumerService:
    """Service for consumer operations."""

    def __init__(self):
        self.repo = ConsumerRepository()

    async def register_consumer(
        self,
        db: AsyncSession,
        data: ConsumerCreate
    ) -> ConsumerResponse:
        """Register a new consumer (user who wants to receive AI comments)."""
        # Check if Instagram ID already registered
        existing = await self.repo.get_by_instagram_id(db, data.instagram_id)
        if existing:
            if existing.is_active:
                raise HTTPException(
                    status_code=400,
                    detail="Instagram ID already registered as consumer"
                )
            else:
                # Reactivate if previously deactivated
                consumer = await self.repo.update(
                    db,
                    existing.id,
                    is_active=True,
                    comment_tone=data.comment_tone,
                    special_requests=data.special_requests
                )
                return ConsumerResponse.model_validate(consumer)

        # Create new consumer
        consumer = await self.repo.create(
            db,
            instagram_id=data.instagram_id,
            comment_tone=data.comment_tone,
            special_requests=data.special_requests,
            is_active=True
        )

        return ConsumerResponse.model_validate(consumer)

    async def get_all_consumers(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConsumerResponse]:
        """Get all consumers."""
        consumers = await self.repo.get_all(db, skip, limit)
        return [ConsumerResponse.model_validate(c) for c in consumers]

    async def get_active_consumers(
        self,
        db: AsyncSession
    ) -> List[ConsumerResponse]:
        """Get all active consumers."""
        consumers = await self.repo.get_active_consumers(db)
        return [ConsumerResponse.model_validate(c) for c in consumers]

    async def deactivate_consumer(
        self,
        db: AsyncSession,
        consumer_id: int
    ) -> ConsumerResponse:
        """Deactivate a consumer."""
        consumer = await self.repo.deactivate(db, consumer_id)
        if not consumer:
            raise HTTPException(status_code=404, detail="Consumer not found")
        return ConsumerResponse.model_validate(consumer)
