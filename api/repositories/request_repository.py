"""Repository for request by week operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from core.models import RequestByWeek
from api.repositories.base_repository import BaseRepository


class RequestRepository(BaseRepository[RequestByWeek]):
    """Repository for request by week operations."""

    def __init__(self):
        super().__init__(RequestByWeek)

    async def get_by_user_and_week(
        self,
        db: AsyncSession,
        user_id: int,
        week_start: datetime
    ) -> Optional[RequestByWeek]:
        """Get request by user and week start date."""
        result = await db.execute(
            select(RequestByWeek).where(
                and_(
                    RequestByWeek.user_id == user_id,
                    RequestByWeek.week_start_date == week_start
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_week(
        self,
        db: AsyncSession,
        week_start: datetime,
        week_end: datetime
    ) -> List[RequestByWeek]:
        """Get all requests for a specific week."""
        result = await db.execute(
            select(RequestByWeek).where(
                and_(
                    RequestByWeek.week_start_date == week_start,
                    RequestByWeek.week_end_date == week_end
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_username_filter(
        self,
        db: AsyncSession,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestByWeek]:
        """Get requests with optional username filter."""
        from core.models import SnsRaiseUser

        query = select(RequestByWeek).join(SnsRaiseUser)

        if username:
            query = query.where(SnsRaiseUser.username.ilike(f"%{username}%"))

        query = query.order_by(RequestByWeek.request_date.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(
        self,
        db: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestByWeek]:
        """Get requests by status."""
        result = await db.execute(
            select(RequestByWeek)
            .where(RequestByWeek.status == status)
            .order_by(RequestByWeek.request_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_comment_count(
        self,
        db: AsyncSession,
        id: int,
        comment_count: int
    ) -> Optional[RequestByWeek]:
        """Update comment count for a request."""
        request = await self.get_by_id(db, id)
        if not request:
            return None

        request.comment_count = comment_count
        request.status = "completed" if comment_count > 0 else "pending"
        await db.flush()
        await db.refresh(request)
        return request
