"""Public API routes (no authentication required)."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.schemas.announcement import AnnouncementResponse
from core.schemas.user import RequestByWeekResponse, UserActionVerificationResponse
from core.schemas.consumer import ConsumerCreate, ConsumerResponse
from core.schemas.producer import ProducerCreate, ProducerResponse, UnfollowCheckRequest, UnfollowCheckResponse
from core.db import announcement_db, user_db, consumer_db, producer_db
from core.services import instagram_service


router = APIRouter()


@router.get("/announcements", response_model=list[AnnouncementResponse])
async def get_announcements(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> list[AnnouncementResponse]:
    """
    Get all active announcements.

    Returns:
        List of active announcements
    """
    announcements = await announcement_db.get_active_announcements(db)
    return announcements


@router.get("/request-by-week", response_model=list[RequestByWeekResponse])
async def get_request_by_week(
    db: Annotated[AsyncSession, Depends(get_db)],
    username: str | None = Query(None, description="Filter by username"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
) -> list[RequestByWeekResponse]:
    """
    Get weekly link requests with optional username filter.

    Args:
        username: Optional username filter
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of weekly requests
    """
    requests = await user_db.get_requests_by_week(db, username, limit, offset)
    return requests


@router.get("/user-action-verification", response_model=list[UserActionVerificationResponse])
async def get_user_action_verification(
    db: Annotated[AsyncSession, Depends(get_db)],
    username: str | None = Query(None, description="Filter by username"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
) -> list[UserActionVerificationResponse]:
    """
    Get user action verification data with optional username filter.

    Args:
        username: Optional username filter
        limit: Maximum number of results
        offset: Number of results to skip

    Returns:
        List of verification records
    """
    verifications = await user_db.get_user_action_verifications(db, username, limit, offset)
    return verifications


@router.post("/consumer", response_model=ConsumerResponse, status_code=status.HTTP_201_CREATED)
async def register_consumer(
    data: ConsumerCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ConsumerResponse:
    """
    Register for AI auto-comment receiving.

    Args:
        data: Consumer registration data

    Returns:
        Created consumer record

    Raises:
        HTTPException: If consumer already exists
    """
    # Check if consumer already exists
    existing = await consumer_db.get_consumer_by_username(db, data.instagram_username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consumer already registered"
        )

    consumer = await consumer_db.create_consumer(db, data.instagram_username)
    return consumer


@router.post("/producer", response_model=ProducerResponse, status_code=status.HTTP_201_CREATED)
async def register_producer(
    data: ProducerCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProducerResponse:
    """
    Register for AI auto-comment providing.

    Args:
        data: Producer registration data

    Returns:
        Created producer record

    Raises:
        HTTPException: If producer already exists or login fails
    """
    try:
        result = await instagram_service.register_producer_account(
            db,
            data.instagram_username,
            data.instagram_password,
            data.verification_code
        )
        # Get the created producer
        producer = await producer_db.get_producer_by_username(db, data.instagram_username)
        return producer
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/unfollow-checker", response_model=UnfollowCheckResponse)
async def check_unfollowers(
    data: UnfollowCheckRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UnfollowCheckResponse:
    """
    Check who doesn't follow back.

    Args:
        data: Unfollow check request data

    Returns:
        List of unfollowers

    Raises:
        HTTPException: If check fails
    """
    try:
        unfollowers = await instagram_service.check_unfollowers(
            db,
            data.instagram_username,
            data.instagram_password,
            data.verification_code,
            use_helper=True
        )
        return UnfollowCheckResponse(
            username=data.instagram_username,
            unfollowers=unfollowers,
            unfollowers_count=len(unfollowers)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to check unfollowers: {str(e)}"
        )
