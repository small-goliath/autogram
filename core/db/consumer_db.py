"""Database access layer for consumer operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Consumer


async def get_consumer_by_username(db: AsyncSession, username: str) -> Consumer | None:
    """
    Get consumer by Instagram username.

    Args:
        db: Database session
        username: Instagram username

    Returns:
        Consumer instance or None if not found
    """
    result = await db.execute(select(Consumer).where(Consumer.instagram_username == username))
    return result.scalar_one_or_none()


async def create_consumer(db: AsyncSession, instagram_username: str) -> Consumer:
    """
    Create new consumer.

    Args:
        db: Database session
        instagram_username: Instagram username

    Returns:
        Created Consumer instance
    """
    consumer = Consumer(instagram_username=instagram_username)
    db.add(consumer)
    await db.flush()
    await db.refresh(consumer)
    return consumer


async def delete_consumer(db: AsyncSession, instagram_username: str) -> bool:
    """
    Delete consumer.

    Args:
        db: Database session
        instagram_username: Instagram username

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(select(Consumer).where(Consumer.instagram_username == instagram_username))
    consumer = result.scalar_one_or_none()
    if consumer:
        await db.delete(consumer)
        await db.flush()
        return True
    return False
