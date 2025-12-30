"""Public API routes (no authentication required)."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.schemas.announcement import AnnouncementResponse
from core.schemas.user import RequestByWeekResponse, UserActionVerificationResponse
from core.schemas.consumer import ConsumerCreate, ConsumerResponse
from core.schemas.producer import ProducerCreate, ProducerResponse, UnfollowCheckRequest, UnfollowCheckResponse
from core.schemas.unfollower_service_user import UnfollowerServiceUserCreate, UnfollowerServiceUserResponse
from core.db import announcement_db, user_db, consumer_db, producer_db, unfollower_service_user_db, unfollower_db
from core.services import instagram_service
from core.crypto import encrypt_data


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


@router.post("/unfollower-service/register", response_model=UnfollowerServiceUserResponse, status_code=status.HTTP_201_CREATED)
async def register_unfollower_service_user(
    data: UnfollowerServiceUserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UnfollowerServiceUserResponse:
    """
    Register user for unfollower service.

    Args:
        data: User registration data

    Returns:
        Registration confirmation

    Raises:
        HTTPException: If user already exists or sns_raise_user doesn't exist
    """
    # Check if user already registered
    existing = await unfollower_service_user_db.get_unfollower_service_user_by_username(db, data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 사용자입니다."
        )

    # Check if sns_raise_user exists
    sns_user = await user_db.get_sns_user_by_username(db, data.username)
    if not sns_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SNS 품앗이 사용자로 먼저 등록해주세요."
        )

    try:
        # Encrypt sensitive data
        encrypted_password = encrypt_data(data.password)
        encrypted_totp_secret = encrypt_data(data.totp_secret) if data.totp_secret else None

        # Create user
        await unfollower_service_user_db.create_unfollower_service_user(
            db,
            data.username,
            encrypted_password,
            encrypted_totp_secret
        )
        await db.commit()

        return UnfollowerServiceUserResponse(
            username=data.username,
            message="언팔로워 검색 서비스에 성공적으로 등록되었습니다."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"등록에 실패했습니다: {str(e)}"
        )


@router.get("/unfollowers/{owner}")
async def get_unfollowers(
    owner: str,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get unfollowers for a specific owner.

    Args:
        owner: Instagram username (owner)

    Returns:
        List of unfollowers

    Raises:
        HTTPException: If owner not registered in unfollower service
    """
    # Check if owner exists in unfollower_service_user
    service_user = await unfollower_service_user_db.get_unfollower_service_user_by_username(db, owner)
    if not service_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="언팔로워 서비스에 등록되지 않은 사용자입니다."
        )

    try:
        unfollowers = await unfollower_db.get_unfollowers_by_owner(db, owner)

        return {
            "owner": owner,
            "count": len(unfollowers),
            "unfollowers": [
                {
                    "unfollower_username": u.unfollower_username,
                    "unfollower_fullname": u.unfollower_fullname,
                    "unfollower_profile_url": u.unfollower_profile_url,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                    "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                }
                for u in unfollowers
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"언팔로워 조회에 실패했습니다: {str(e)}"
        )
