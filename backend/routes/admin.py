"""Admin API routes (JWT authentication required)."""
from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_admin
from core.schemas.admin import AdminLogin, AdminToken
from core.schemas.user import SnsUserCreate, SnsUserUpdate, SnsUserResponse
from core.schemas.helper import HelperCreate, HelperResponse
from core.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from core.db import user_db, helper_db, announcement_db
from core.services import admin_service, instagram_service

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = APIRouter()


@router.post("/login", response_model=AdminToken)
async def admin_login(
    data: AdminLogin,
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AdminToken:
    """
    Admin login endpoint.

    Args:
        data: Admin login credentials

    Returns:
        JWT access token

    Raises:
        HTTPException: If authentication fails
    """
    admin = await admin_service.authenticate_admin(db, data.username, data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = admin_service.create_access_token(data={"sub": admin["username"]})
    return AdminToken(access_token=access_token)


# SNS User Management
@router.get("/sns-users")
async def list_sns_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)],
    page: int = 1,
    limit: int = 20,
    search: str = ""
) -> dict:
    """
    List all SNS users with pagination and search.

    Args:
        page: Page number (1-indexed)
        limit: Number of items per page
        search: Search query for username

    Returns:
        Dict with users list and pagination info
    """
    offset = (page - 1) * limit
    users, total_count = await user_db.get_sns_users_paginated(db, limit, offset, search)
    total_pages = (total_count + limit - 1) // limit

    # Convert SQLAlchemy models to Pydantic models
    user_responses = [SnsUserResponse.model_validate(user) for user in users]

    return {
        "users": user_responses,
        "total": total_count,
        "total_pages": total_pages,
        "current_page": page
    }


@router.post("/sns-users", response_model=SnsUserResponse, status_code=status.HTTP_201_CREATED)
async def create_sns_user(
    data: SnsUserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> SnsUserResponse:
    """
    Create new SNS user.

    Args:
        data: SNS user data

    Returns:
        Created SNS user

    Raises:
        HTTPException: If username already exists
    """
    # Check if username exists
    existing = await user_db.get_sns_user_by_username(db, data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user = await user_db.create_sns_user(db, data.username)
    return user


@router.put("/sns-users/{user_id}", response_model=SnsUserResponse)
async def update_sns_user(
    user_id: int,
    data: SnsUserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> SnsUserResponse:
    """
    Update SNS user.

    Args:
        user_id: User ID
        data: Updated user data

    Returns:
        Updated SNS user

    Raises:
        HTTPException: If user not found or username already exists
    """
    # Check if new username is taken by another user
    existing = await user_db.get_sns_user_by_username(db, data.username)
    if existing and existing.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user = await user_db.update_sns_user(db, user_id, data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.delete("/sns-users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sns_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> None:
    """
    Delete SNS user (CASCADE delete related records).

    Args:
        user_id: User ID

    Raises:
        HTTPException: If user not found
    """
    success = await user_db.delete_sns_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


# Helper Account Management
@router.get("/helpers", response_model=list[HelperResponse])
async def list_helpers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> list[HelperResponse]:
    """
    List all helper accounts.

    Returns:
        List of helper accounts
    """
    helpers = await helper_db.get_all_helpers(db)
    return helpers


@router.post("/helpers", response_model=HelperResponse, status_code=status.HTTP_201_CREATED)
async def register_helper(
    data: HelperCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> HelperResponse:
    """
    Register new helper account with Instagram login verification.

    Args:
        data: Helper account data

    Returns:
        Created helper account

    Raises:
        HTTPException: If helper already exists or Instagram login fails
    """
    logger.info(f"Attempting to register helper account: {data.instagram_username}")

    # Check if helper already exists
    existing = await helper_db.get_helper_by_username(db, data.instagram_username)
    if existing:
        logger.warning(f"Helper account already exists: {data.instagram_username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 헬퍼 계정입니다"
        )

    try:
        # Verify Instagram login and register helper
        logger.info(f"Verifying Instagram login for: {data.instagram_username}")
        result = await instagram_service.register_helper_account(
            db,
            data.instagram_username,
            data.instagram_password,
            data.verification_code
        )

        # Get the created helper from database
        helper = await helper_db.get_helper_by_username(db, data.instagram_username)
        if not helper:
            logger.error(f"Helper created but not found in database: {data.instagram_username}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="헬퍼 계정 생성에 실패했습니다"
            )

        logger.info(f"Successfully registered helper account: {data.instagram_username}")
        return helper
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        error_msg = str(e)
        logger.error(f"Failed to register helper account {data.instagram_username}: {error_msg}", exc_info=True)

        # Provide more user-friendly error messages
        if "login" in error_msg.lower() or "password" in error_msg.lower():
            detail = "인스타그램 로그인에 실패했습니다. 사용자명과 비밀번호를 확인해주세요."
        elif "verification" in error_msg.lower() or "code" in error_msg.lower():
            detail = "2단계 인증 코드가 필요합니다."
        else:
            detail = f"헬퍼 계정 등록 실패: {error_msg}"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


@router.patch("/helpers/{helper_id}", response_model=HelperResponse)
async def update_helper(
    helper_id: int,
    data: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> HelperResponse:
    """
    Update helper account (e.g., toggle is_active status).

    Args:
        helper_id: Helper ID
        data: Updated helper data

    Returns:
        Updated helper account

    Raises:
        HTTPException: If helper not found
    """
    helper = await helper_db.update_helper_status(db, helper_id, data.get('is_active'))
    if not helper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Helper not found"
        )
    return helper


@router.delete("/helpers/{helper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_helper(
    helper_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> None:
    """
    Delete helper account.

    Args:
        helper_id: Helper ID

    Raises:
        HTTPException: If helper not found
    """
    success = await helper_db.delete_helper(db, helper_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Helper not found"
        )


# Announcement Management
@router.get("/announcements", response_model=list[AnnouncementResponse])
async def list_all_announcements(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> list[AnnouncementResponse]:
    """
    List all announcements (including inactive).

    Returns:
        List of all announcements
    """
    announcements = await announcement_db.get_all_announcements(db)
    return announcements


@router.post("/announcements", response_model=AnnouncementResponse, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    data: AnnouncementCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> AnnouncementResponse:
    """
    Create new announcement.

    Args:
        data: Announcement data

    Returns:
        Created announcement
    """
    announcement = await announcement_db.create_announcement(
        db,
        title=data.title,
        content=data.content,
        kakao_openchat_link=data.kakao_openchat_link,
        kakao_qr_code_url=data.kakao_qr_code_url,
        is_active=data.is_active
    )
    return announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    data: AnnouncementUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> AnnouncementResponse:
    """
    Update announcement.

    Args:
        announcement_id: Announcement ID
        data: Updated announcement data

    Returns:
        Updated announcement

    Raises:
        HTTPException: If announcement not found
    """
    announcement = await announcement_db.update_announcement(
        db,
        announcement_id,
        title=data.title,
        content=data.content,
        kakao_openchat_link=data.kakao_openchat_link,
        kakao_qr_code_url=data.kakao_qr_code_url,
        is_active=data.is_active
    )
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )

    return announcement


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[dict, Depends(get_current_admin)]
) -> None:
    """
    Delete announcement.

    Args:
        announcement_id: Announcement ID

    Raises:
        HTTPException: If announcement not found
    """
    success = await announcement_db.delete_announcement(db, announcement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
