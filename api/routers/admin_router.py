"""Admin router for authentication and user management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.schemas import (
    AdminLogin,
    TokenResponse,
    AdminResponse,
    SnsRaiseUserCreate,
    SnsRaiseUserUpdate,
    SnsRaiseUserResponse,
    HelperCreate,
    HelperResponse,
    MessageResponse
)
from api.dependencies import get_current_admin, get_current_superadmin
from api.services.admin_service import AdminService
from api.services.sns_user_service import SnsUserService
from api.services.helper_service import HelperService

router = APIRouter()

# Services
admin_service = AdminService()
sns_user_service = SnsUserService()
helper_service = HelperService()


# Admin Authentication
@router.post("/login", response_model=TokenResponse)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Admin login endpoint."""
    login_data = AdminLogin(username=form_data.username, password=form_data.password)
    result = await admin_service.login(db, login_data)
    return result


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get current admin information."""
    admin = await admin_service.get_current_admin(db, current_admin["username"])
    return admin


# SNS User Management
@router.get("/sns-users", response_model=List[SnsRaiseUserResponse])
async def get_all_sns_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all SNS users."""
    users = await sns_user_service.get_all_users(db, skip, limit)
    return users


@router.get("/sns-users/{user_id}", response_model=SnsRaiseUserResponse)
async def get_sns_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get SNS user by ID."""
    user = await sns_user_service.get_user_by_id(db, user_id)
    return user


@router.post("/sns-users", response_model=SnsRaiseUserResponse)
async def create_sns_user(
    data: SnsRaiseUserCreate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new SNS user."""
    user = await sns_user_service.create_user(db, data)
    return user


@router.put("/sns-users/{user_id}", response_model=SnsRaiseUserResponse)
async def update_sns_user(
    user_id: int,
    data: SnsRaiseUserUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an SNS user."""
    user = await sns_user_service.update_user(db, user_id, data)
    return user


@router.delete("/sns-users/{user_id}", response_model=MessageResponse)
async def delete_sns_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an SNS user (cascade delete all related data)."""
    result = await sns_user_service.delete_user(db, user_id)
    return result


# Helper Account Management
@router.get("/helpers", response_model=List[HelperResponse])
async def get_all_helpers(
    skip: int = 0,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all helper accounts."""
    helpers = await helper_service.get_all_helpers(db, skip, limit)
    return helpers


@router.post("/helpers", response_model=HelperResponse)
async def create_helper(
    data: HelperCreate,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Register a new helper account (login to Instagram and save session)."""
    helper = await helper_service.create_helper(db, data)
    return helper


@router.delete("/helpers/{helper_id}", response_model=MessageResponse)
async def delete_helper(
    helper_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a helper account."""
    result = await helper_service.delete_helper(db, helper_id)
    return result
