"""Database access layer for SNS user operations."""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import SnsRaiseUser, RequestByWeek, UserActionVerification


async def get_all_sns_users(db: AsyncSession) -> list[SnsRaiseUser]:
    """
    Get all SNS users.

    Args:
        db: Database session

    Returns:
        List of SnsRaiseUser instances
    """
    result = await db.execute(
        select(SnsRaiseUser).order_by(SnsRaiseUser.created_at.desc())
    )
    return list(result.scalars().all())


async def get_sns_users_paginated(
    db: AsyncSession, limit: int = 20, offset: int = 0, search: str = ""
) -> tuple[list[SnsRaiseUser], int]:
    """
    Get SNS users with pagination and search.

    Args:
        db: Database session
        limit: Maximum number of results
        offset: Number of results to skip
        search: Search query for username

    Returns:
        Tuple of (list of SnsRaiseUser instances, total count)
    """
    query = select(SnsRaiseUser)

    if search:
        query = query.where(SnsRaiseUser.username.ilike(f"%{search}%"))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_count = await db.scalar(count_query)

    # Get paginated results
    query = query.order_by(SnsRaiseUser.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    users = list(result.scalars().all())

    return users, total_count or 0


async def get_sns_user_by_id(db: AsyncSession, user_id: int) -> SnsRaiseUser | None:
    """
    Get SNS user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        SnsRaiseUser instance or None if not found
    """
    result = await db.execute(select(SnsRaiseUser).where(SnsRaiseUser.id == user_id))
    return result.scalar_one_or_none()


async def get_sns_user_by_username(
    db: AsyncSession, username: str
) -> SnsRaiseUser | None:
    """
    Get SNS user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        SnsRaiseUser instance or None if not found
    """
    result = await db.execute(
        select(SnsRaiseUser).where(SnsRaiseUser.username == username)
    )
    return result.scalar_one_or_none()


async def create_sns_user(db: AsyncSession, username: str) -> SnsRaiseUser:
    """
    Create new SNS user.

    Args:
        db: Database session
        username: Username

    Returns:
        Created SnsRaiseUser instance
    """
    user = SnsRaiseUser(username=username)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_sns_user(
    db: AsyncSession, user_id: int, username: str
) -> SnsRaiseUser | None:
    """
    Update SNS user.

    Args:
        db: Database session
        user_id: User ID
        username: New username

    Returns:
        Updated SnsRaiseUser instance or None if not found
    """
    user = await get_sns_user_by_id(db, user_id)
    if user:
        user.username = username
        await db.flush()
        await db.refresh(user)
    return user


async def delete_sns_user(db: AsyncSession, user_id: int) -> bool:
    """
    Delete SNS user (CASCADE delete related records).

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = await get_sns_user_by_id(db, user_id)
    if user:
        await db.delete(user)
        await db.flush()
        return True
    return False


async def get_requests_by_week(
    db: AsyncSession, username: str | None = None, limit: int = 100, offset: int = 0
) -> list[RequestByWeek]:
    """
    Get weekly requests with optional username filter.

    Args:
        db: Database session
        username: Optional username filter
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of RequestByWeek instances
    """
    query = select(RequestByWeek).order_by(RequestByWeek.created_at.desc())

    if username:
        query = query.where(RequestByWeek.username == username)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_action_verifications(
    db: AsyncSession, username: str | None = None, limit: int = 100, offset: int = 0
) -> list[UserActionVerification]:
    """
    Get user action verifications with optional username filter.

    Args:
        db: Database session
        username: Optional username filter
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of UserActionVerification instances
    """
    query = select(UserActionVerification).order_by(
        UserActionVerification.created_at.desc()
    )

    if username:
        query = query.where(UserActionVerification.username == username)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())
