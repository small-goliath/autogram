"""Database access layer for admin operations."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Admin


async def get_admin_by_username(db: AsyncSession, username: str) -> Admin | None:
    """
    Get admin by username.

    Args:
        db: Database session
        username: Admin username

    Returns:
        Admin instance or None if not found
    """
    result = await db.execute(select(Admin).where(Admin.username == username))
    return result.scalar_one_or_none()


async def create_admin(db: AsyncSession, username: str, hashed_password: str) -> Admin:
    """
    Create new admin.

    Args:
        db: Database session
        username: Admin username
        hashed_password: Hashed password

    Returns:
        Created Admin instance
    """
    admin = Admin(username=username, password=hashed_password)
    db.add(admin)
    await db.flush()
    await db.refresh(admin)
    return admin
