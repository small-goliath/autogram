"""Database access layer for helper operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Helper
from core.utils import get_kst_now


async def get_all_helpers(db: AsyncSession) -> list[Helper]:
    """
    Get all helper accounts.

    Args:
        db: Database session

    Returns:
        List of Helper instances
    """
    result = await db.execute(select(Helper).order_by(Helper.created_at.desc()))
    return list(result.scalars().all())


async def get_helper_by_id(db: AsyncSession, helper_id: int) -> Helper | None:
    """
    Get helper by ID.

    Args:
        db: Database session
        helper_id: Helper ID

    Returns:
        Helper instance or None if not found
    """
    result = await db.execute(select(Helper).where(Helper.id == helper_id))
    return result.scalar_one_or_none()


async def get_helper_by_username(db: AsyncSession, username: str) -> Helper | None:
    """
    Get helper by Instagram username.

    Args:
        db: Database session
        username: Instagram username

    Returns:
        Helper instance or None if not found
    """
    result = await db.execute(select(Helper).where(Helper.instagram_username == username))
    return result.scalar_one_or_none()


async def get_active_helper(db: AsyncSession) -> Helper | None:
    """
    Get an active helper account for use.

    Args:
        db: Database session

    Returns:
        Helper instance or None if no active helper available
    """
    result = await db.execute(
        select(Helper)
        .where(Helper.is_active == True)
        .order_by(Helper.last_used_at.asc().nulls_first())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_helper(
    db: AsyncSession,
    instagram_username: str,
    instagram_password: str,
    session_data: str | None = None
) -> Helper:
    """
    Create new helper account.

    Args:
        db: Database session
        instagram_username: Instagram username
        instagram_password: Encrypted Instagram password
        session_data: Encrypted session data

    Returns:
        Created Helper instance
    """
    helper = Helper(
        instagram_username=instagram_username,
        instagram_password=instagram_password,
        session_data=session_data,
        is_active=True,
    )
    db.add(helper)
    await db.flush()
    await db.refresh(helper)
    return helper


async def update_helper_session(
    db: AsyncSession,
    helper_id: int,
    session_data: str
) -> Helper | None:
    """
    Update helper session data.

    Args:
        db: Database session
        helper_id: Helper ID
        session_data: Encrypted session data

    Returns:
        Updated Helper instance or None if not found
    """
    helper = await get_helper_by_id(db, helper_id)
    if helper:
        helper.session_data = session_data
        helper.last_used_at = get_kst_now()
        await db.flush()
        await db.refresh(helper)
    return helper


async def update_helper_last_used(db: AsyncSession, helper_id: int) -> Helper | None:
    """
    Update helper last used timestamp.

    Args:
        db: Database session
        helper_id: Helper ID

    Returns:
        Updated Helper instance or None if not found
    """
    helper = await get_helper_by_id(db, helper_id)
    if helper:
        helper.last_used_at = get_kst_now()
        await db.flush()
        await db.refresh(helper)
    return helper


async def update_helper_status(
    db: AsyncSession,
    helper_id: int,
    is_active: bool
) -> Helper | None:
    """
    Update helper active status.

    Args:
        db: Database session
        helper_id: Helper ID
        is_active: New active status

    Returns:
        Updated Helper instance or None if not found
    """
    helper = await get_helper_by_id(db, helper_id)
    if helper:
        helper.is_active = is_active
        await db.flush()
        await db.refresh(helper)
    return helper


async def delete_helper(db: AsyncSession, helper_id: int) -> bool:
    """
    Delete helper account.

    Args:
        db: Database session
        helper_id: Helper ID

    Returns:
        True if deleted, False if not found
    """
    helper = await get_helper_by_id(db, helper_id)
    if helper:
        await db.delete(helper)
        await db.flush()
        return True
    return False
