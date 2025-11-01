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
    verification_code: str | None = None,
    session_data: str | None = None
) -> Producer:
    """
    Create new producer.

    Args:
        db: Database session
        instagram_username: Instagram username
        instagram_password: Encrypted Instagram password
        verification_code: Optional 2FA verification code
        session_data: Encrypted session data

    Returns:
        Created Producer instance
    """
    producer = Producer(
        instagram_username=instagram_username,
        instagram_password=instagram_password,
        verification_code=verification_code,
        session_data=session_data,
    )
    db.add(producer)
    await db.flush()
    await db.refresh(producer)
    return producer


async def update_producer_session(
    db: AsyncSession,
    producer_id: int,
    session_data: str
) -> Producer | None:
    """
    Update producer session data.

    Args:
        db: Database session
        producer_id: Producer ID
        session_data: Encrypted session data

    Returns:
        Updated Producer instance or None if not found
    """
    result = await db.execute(select(Producer).where(Producer.id == producer_id))
    producer = result.scalar_one_or_none()
    if producer:
        producer.session_data = session_data
        producer.last_used_at = datetime.utcnow()
        await db.flush()
        await db.refresh(producer)
    return producer
