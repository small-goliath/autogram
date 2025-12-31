"""Database access layer for unfollower service user operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import UnfollowerServiceUser


async def get_unfollower_service_user_by_username(
    db: AsyncSession, username: str
) -> UnfollowerServiceUser | None:
    """
    Get unfollower service user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        UnfollowerServiceUser instance or None if not found
    """
    result = await db.execute(
        select(UnfollowerServiceUser).where(UnfollowerServiceUser.username == username)
    )
    return result.scalar_one_or_none()


async def create_unfollower_service_user(
    db: AsyncSession, username: str, password: str, totp_secret: str | None = None
) -> UnfollowerServiceUser:
    """
    Create new unfollower service user.

    Args:
        db: Database session
        username: Username (must exist in sns_raise_user)
        password: Encrypted password
        totp_secret: Optional encrypted TOTP secret

    Returns:
        Created UnfollowerServiceUser instance
    """
    user = UnfollowerServiceUser(
        username=username, password=password, totp_secret=totp_secret
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_unfollower_service_user(
    db: AsyncSession, username: str, password: str, totp_secret: str | None = None
) -> UnfollowerServiceUser | None:
    """
    Update unfollower service user credentials.

    Args:
        db: Database session
        username: Username
        password: New encrypted password
        totp_secret: Optional new encrypted TOTP secret

    Returns:
        Updated UnfollowerServiceUser instance or None if not found
    """
    result = await db.execute(
        select(UnfollowerServiceUser).where(UnfollowerServiceUser.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        user.password = password
        user.totp_secret = totp_secret
        await db.flush()
        await db.refresh(user)
    return user


async def delete_unfollower_service_user(db: AsyncSession, username: str) -> bool:
    """
    Delete unfollower service user.

    Args:
        db: Database session
        username: Username

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(
        select(UnfollowerServiceUser).where(UnfollowerServiceUser.username == username)
    )
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.flush()
        return True
    return False
