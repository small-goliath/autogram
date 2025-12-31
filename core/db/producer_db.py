"""Database access layer for producer operations."""
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Producer


async def get_producer_by_username(db: AsyncSession, username: str) -> Producer | None:
    """
    Get producer by Instagram username.

    Args:
        db: Database session
        username: Instagram username

    Returns:
        Producer instance or None if not found
    """
    result = await db.execute(select(Producer).where(Producer.instagram_username == username))
    return result.scalar_one_or_none()


async def get_active_producer(db: AsyncSession) -> Producer | None:
    """
    Get an active producer account for use.

    Args:
        db: Database session

    Returns:
        Producer instance or None if no active producer available
    """
    result = await db.execute(
        select(Producer)
        .where(Producer.status == "active")
        .order_by(Producer.last_used_at.asc().nulls_first())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_producer(
    db: AsyncSession,
    instagram_username: str,
    instagram_password: str,
    totp_secret: str | None = None
) -> Producer:
    """
    Create new producer.

    Args:
        db: Database session
        instagram_username: Instagram username
        instagram_password: Encrypted Instagram password
        totp_secret: Optional encrypted TOTP secret for 2FA

    Returns:
        Created Producer instance
    """
    producer = Producer(
        instagram_username=instagram_username,
        instagram_password=instagram_password,
        totp_secret=totp_secret,
    )
    db.add(producer)
    await db.flush()
    await db.refresh(producer)
    return producer


async def update_producer_last_used(
    db: AsyncSession,
    instagram_username: str
) -> Producer | None:
    """
    Update producer last used timestamp.

    Args:
        db: Database session
        instagram_username: Instagram username

    Returns:
        Updated Producer instance or None if not found
    """
    result = await db.execute(select(Producer).where(Producer.instagram_username == instagram_username))
    producer = result.scalar_one_or_none()
    if producer:
        producer.last_used_at = datetime.utcnow()
        await db.flush()
        await db.refresh(producer)
    return producer


async def delete_producer(
    db: AsyncSession,
    instagram_username: str
) -> bool:
    """
    Delete producer.

    Args:
        db: Database session
        instagram_username: Instagram username

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(select(Producer).where(Producer.instagram_username == instagram_username))
    producer = result.scalar_one_or_none()
    if producer:
        await db.delete(producer)
        await db.flush()
        return True
    return False
