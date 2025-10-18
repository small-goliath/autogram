"""Public router for non-authenticated endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.schemas import (
    RequestByWeekResponse,
    UserActionVerificationResponse,
    ConsumerCreate,
    ConsumerResponse,
    ProducerCreate,
    ProducerResponse,
    UnfollowCheckerRequest,
    UnfollowCheckerResponse
)
from api.services.request_service import RequestService
from api.services.verification_service import VerificationService
from api.services.consumer_service import ConsumerService
from api.services.producer_service import ProducerService
from api.services.instagram_service import InstagramService
from api.services.notice_service import NoticeService

router = APIRouter()

# Services
request_service = RequestService()
verification_service = VerificationService()
consumer_service = ConsumerService()
producer_service = ProducerService()
instagram_service = InstagramService()
notice_service = NoticeService()


# Notices
@router.get("/notices")
async def get_notices(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get recent notices with KakaoTalk information."""
    result = await notice_service.get_notices_with_kakaotalk_info(db, limit)
    return result


# Last Week Status
@router.get("/requests-by-week", response_model=List[RequestByWeekResponse])
async def get_requests_by_week(
    username: Optional[str] = Query(default=None, description="Filter by username"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly requests with optional username filter."""
    requests = await request_service.get_all_requests(db, username, skip, limit)
    return requests


# Exchange Status
@router.get("/user-action-verification", response_model=List[UserActionVerificationResponse])
async def get_user_action_verification(
    username: Optional[str] = Query(default=None, description="Filter by username"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get user action verifications with optional username filter."""
    verifications = await verification_service.get_all_verifications(db, username, skip, limit)
    return verifications


# AI Comment - Consumer Registration
@router.post("/consumer", response_model=ConsumerResponse)
async def register_consumer(
    data: ConsumerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register as a consumer (receive AI comments)."""
    consumer = await consumer_service.register_consumer(db, data)
    return consumer


# AI Comment - Producer Registration
@router.post("/producer", response_model=ProducerResponse)
async def register_producer(
    data: ProducerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register as a producer (provide account for AI comments)."""
    producer = await producer_service.register_producer(db, data)
    return producer


# Unfollow Checker
@router.post("/unfollow-checker", response_model=UnfollowCheckerResponse)
async def check_unfollowers(
    data: UnfollowCheckerRequest,
    db: AsyncSession = Depends(get_db)
):
    """Check unfollowers for an Instagram account."""
    result = await instagram_service.check_unfollowers(db, data)
    return result
