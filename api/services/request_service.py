"""Request service for weekly request management."""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import RequestByWeekCreate, RequestByWeekResponse
from api.repositories.request_repository import RequestRepository


class RequestService:
    """Service for request by week operations."""

    def __init__(self):
        self.repo = RequestRepository()

    def get_week_dates(self, date: datetime) -> tuple[datetime, datetime]:
        """
        Calculate week start and end dates (Monday to Sunday).

        Args:
            date: Any date within the week

        Returns:
            Tuple of (week_start, week_end)
        """
        # Get Monday of the week
        week_start = date - timedelta(days=date.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        # Get Sunday of the week
        week_end = week_start + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        return week_start, week_end

    async def get_all_requests(
        self,
        db: AsyncSession,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequestByWeekResponse]:
        """Get all requests with optional username filter."""
        requests = await self.repo.get_by_username_filter(db, username, skip, limit)
        return [RequestByWeekResponse.model_validate(r) for r in requests]

    async def get_request_by_id(
        self,
        db: AsyncSession,
        request_id: int
    ) -> RequestByWeekResponse:
        """Get request by ID."""
        request = await self.repo.get_by_id(db, request_id)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return RequestByWeekResponse.model_validate(request)

    async def create_request(
        self,
        db: AsyncSession,
        data: RequestByWeekCreate
    ) -> RequestByWeekResponse:
        """Create a new weekly request."""
        from api.repositories.sns_user_repository import SnsUserRepository

        # Verify user exists
        user_repo = SnsUserRepository()
        user = await user_repo.get_by_id(db, data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user already submitted for this week
        existing = await self.repo.get_by_user_and_week(
            db,
            data.user_id,
            data.week_start_date
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already submitted a request for this week"
            )

        # Create request
        request = await self.repo.create(
            db,
            user_id=data.user_id,
            instagram_link=data.instagram_link,
            week_start_date=data.week_start_date,
            week_end_date=data.week_end_date,
            status="pending",
            comment_count=0
        )

        return RequestByWeekResponse.model_validate(request)

    async def get_requests_by_week(
        self,
        db: AsyncSession,
        week_start: datetime,
        week_end: datetime
    ) -> List[RequestByWeekResponse]:
        """Get all requests for a specific week."""
        requests = await self.repo.get_by_week(db, week_start, week_end)
        return [RequestByWeekResponse.model_validate(r) for r in requests]

    async def get_current_week_requests(
        self,
        db: AsyncSession
    ) -> List[RequestByWeekResponse]:
        """Get all requests for current week."""
        now = datetime.utcnow()
        week_start, week_end = self.get_week_dates(now)
        return await self.get_requests_by_week(db, week_start, week_end)

    async def update_comment_count(
        self,
        db: AsyncSession,
        request_id: int,
        comment_count: int
    ) -> RequestByWeekResponse:
        """Update comment count for a request."""
        request = await self.repo.update_comment_count(db, request_id, comment_count)
        if not request:
            raise HTTPException(status_code=404, detail="Request not found")
        return RequestByWeekResponse.model_validate(request)
