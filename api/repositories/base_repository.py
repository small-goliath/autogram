"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        db.add(instance)
        await db.flush()
        await db.refresh(instance)
        return instance

    async def update(self, db: AsyncSession, id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        instance = await self.get_by_id(db, id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)

        await db.flush()
        await db.refresh(instance)
        return instance

    async def delete(self, db: AsyncSession, id: int) -> bool:
        """Delete a record by ID."""
        result = await db.execute(delete(self.model).where(self.model.id == id))
        return result.rowcount > 0

    async def count(self, db: AsyncSession) -> int:
        """Count total records."""
        from sqlalchemy import func
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
