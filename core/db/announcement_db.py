"""Database access layer for announcement operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Announcement


async def get_active_announcements(db: AsyncSession) -> list[Announcement]:
    """
    Get all active announcements.

    Args:
        db: Database session

    Returns:
        List of active Announcement instances
    """
    result = await db.execute(
        select(Announcement)
        .where(Announcement.is_active)
        .order_by(Announcement.created_at.desc())
    )
    return list(result.scalars().all())


async def get_all_announcements(db: AsyncSession) -> list[Announcement]:
    """
    Get all announcements (admin view).

    Args:
        db: Database session

    Returns:
        List of Announcement instances
    """
    result = await db.execute(
        select(Announcement).order_by(Announcement.created_at.desc())
    )
    return list(result.scalars().all())


async def get_announcement_by_id(
    db: AsyncSession, announcement_id: int
) -> Announcement | None:
    """
    Get announcement by ID.

    Args:
        db: Database session
        announcement_id: Announcement ID

    Returns:
        Announcement instance or None if not found
    """
    result = await db.execute(
        select(Announcement).where(Announcement.id == announcement_id)
    )
    return result.scalar_one_or_none()


async def create_announcement(
    db: AsyncSession,
    title: str,
    content: str,
    kakao_openchat_link: str | None = None,
    kakao_qr_code_url: str | None = None,
    is_active: bool = True,
) -> Announcement:
    """
    Create new announcement.

    Args:
        db: Database session
        title: Announcement title
        content: Announcement content
        kakao_openchat_link: Optional Kakao openchat link
        kakao_qr_code_url: Optional Kakao QR code URL
        is_active: Whether announcement is active

    Returns:
        Created Announcement instance
    """
    announcement = Announcement(
        title=title,
        content=content,
        kakao_openchat_link=kakao_openchat_link,
        kakao_qr_code_url=kakao_qr_code_url,
        is_active=is_active,
    )
    db.add(announcement)
    await db.flush()
    await db.refresh(announcement)
    return announcement


async def update_announcement(
    db: AsyncSession,
    announcement_id: int,
    title: str | None = None,
    content: str | None = None,
    kakao_openchat_link: str | None = None,
    kakao_qr_code_url: str | None = None,
    is_active: bool | None = None,
) -> Announcement | None:
    """
    Update announcement.

    Args:
        db: Database session
        announcement_id: Announcement ID
        title: Optional new title
        content: Optional new content
        kakao_openchat_link: Optional new Kakao openchat link
        kakao_qr_code_url: Optional new Kakao QR code URL
        is_active: Optional new active status

    Returns:
        Updated Announcement instance or None if not found
    """
    announcement = await get_announcement_by_id(db, announcement_id)
    if announcement:
        if title is not None:
            announcement.title = title
        if content is not None:
            announcement.content = content
        if kakao_openchat_link is not None:
            announcement.kakao_openchat_link = kakao_openchat_link
        if kakao_qr_code_url is not None:
            announcement.kakao_qr_code_url = kakao_qr_code_url
        if is_active is not None:
            announcement.is_active = is_active
        await db.flush()
        await db.refresh(announcement)
    return announcement


async def delete_announcement(db: AsyncSession, announcement_id: int) -> bool:
    """
    Delete announcement.

    Args:
        db: Database session
        announcement_id: Announcement ID

    Returns:
        True if deleted, False if not found
    """
    announcement = await get_announcement_by_id(db, announcement_id)
    if announcement:
        await db.delete(announcement)
        await db.flush()
        return True
    return False
