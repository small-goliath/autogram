"""Business logic for admin operations."""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import get_settings
from core.crypto import hash_password, verify_password
from core.db import admin_db


async def authenticate_admin(db: AsyncSession, username: str, password: str) -> dict | None:
    """
    Authenticate admin and return user info.

    Args:
        db: Database session
        username: Admin username
        password: Admin password

    Returns:
        Admin info dict or None if authentication fails
    """
    admin = await admin_db.get_admin_by_username(db, username)
    if not admin:
        return None

    if not verify_password(password, admin.password):
        return None

    return {"id": admin.id, "username": admin.username}


def create_access_token(data: dict) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token

    Returns:
        JWT token string
    """
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """
    Verify JWT token and return payload.

    Args:
        token: JWT token string

    Returns:
        Token payload dict or None if invalid
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def create_admin_account(db: AsyncSession, username: str, password: str) -> dict:
    """
    Create new admin account.

    Args:
        db: Database session
        username: Admin username
        password: Admin password

    Returns:
        Created admin info dict
    """
    hashed_password = hash_password(password)
    admin = await admin_db.create_admin(db, username, hashed_password)
    return {"id": admin.id, "username": admin.username}
