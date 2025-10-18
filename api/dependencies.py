"""FastAPI dependencies for authentication and authorization."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import verify_token
from api.repositories.admin_repository import AdminRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/py/admin/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get current authenticated admin from JWT token.

    Args:
        token: JWT access token
        db: Database session

    Returns:
        Admin payload from token

    Raises:
        HTTPException: If token is invalid or admin not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    username: Optional[str] = payload.get("sub")
    admin_id: Optional[int] = payload.get("admin_id")

    if username is None or admin_id is None:
        raise credentials_exception

    # Verify admin exists and is active
    admin_repo = AdminRepository()
    admin = await admin_repo.get_by_username(db, username)

    if admin is None:
        raise credentials_exception

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    return {"username": username, "admin_id": admin_id, "is_superadmin": admin.is_superadmin}


async def get_current_superadmin(
    current_admin: dict = Depends(get_current_admin)
) -> dict:
    """
    Ensure current admin is a superadmin.

    Args:
        current_admin: Current authenticated admin

    Returns:
        Admin payload

    Raises:
        HTTPException: If admin is not a superadmin
    """
    if not current_admin.get("is_superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required"
        )

    return current_admin
