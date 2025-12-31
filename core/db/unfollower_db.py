"""Database access layer for unfollower operations."""

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Unfollower


async def upsert_unfollowers(
    db: AsyncSession, owner: str, unfollowers: list[dict]
) -> int:
    """
    Upsert unfollowers (insert or update on conflict).

    Args:
        db: Database session
        owner: Owner username
        unfollowers: List of unfollower data dicts with keys:
                    - unfollower_username
                    - unfollower_fullname
                    - unfollower_profile_url

    Returns:
        Number of unfollowers inserted/updated
    """
    if not unfollowers:
        return 0

    values = [
        {
            "owner": owner,
            "unfollower_username": u["unfollower_username"],
            "unfollower_fullname": u["unfollower_fullname"],
            "unfollower_profile_url": u["unfollower_profile_url"],
        }
        for u in unfollowers
    ]

    stmt = insert(Unfollower).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["owner", "unfollower_username"],
        set_={
            "unfollower_fullname": stmt.excluded.unfollower_fullname,
            "unfollower_profile_url": stmt.excluded.unfollower_profile_url,
        },
    )

    await db.execute(stmt)
    await db.flush()
    return len(values)


async def get_unfollowers_by_owner(db: AsyncSession, owner: str) -> list[Unfollower]:
    """
    Get all unfollowers for a specific owner.

    Args:
        db: Database session
        owner: Owner username

    Returns:
        List of Unfollower instances
    """
    result = await db.execute(select(Unfollower).where(Unfollower.owner == owner))
    return list(result.scalars().all())


async def delete_unfollowers_by_owner(db: AsyncSession, owner: str) -> int:
    """
    Delete all unfollowers for a specific owner.

    Args:
        db: Database session
        owner: Owner username

    Returns:
        Number of deleted records
    """
    result = await db.execute(select(Unfollower).where(Unfollower.owner == owner))
    unfollowers = list(result.scalars().all())
    count = len(unfollowers)

    for unfollower in unfollowers:
        await db.delete(unfollower)

    await db.flush()
    return count
