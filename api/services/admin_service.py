"""Admin service for authentication and management."""
from typing import Optional, Dict
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.security import verify_password, hash_password, create_access_token
from core.schemas import AdminCreate, AdminLogin, AdminResponse
from api.repositories.admin_repository import AdminRepository


class AdminService:
    """Service for admin operations."""

    def __init__(self):
        self.repo = AdminRepository()

    async def login(self, db: AsyncSession, data: AdminLogin) -> Dict[str, str]:
        """
        Authenticate admin and return JWT token.

        Args:
            db: Database session
            data: Login credentials

        Returns:
            Dictionary with access_token and token_type

        Raises:
            HTTPException: If credentials are invalid
        """
        admin = await self.repo.get_by_username(db, data.username)

        if not admin:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(data.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not admin.is_active:
            raise HTTPException(status_code=403, detail="Admin account is inactive")

        # Update last login
        await self.repo.update_last_login(db, admin.id)

        # Create JWT token
        access_token = create_access_token(
            data={"sub": admin.username, "admin_id": admin.id}
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    async def get_current_admin(
        self,
        db: AsyncSession,
        username: str
    ) -> Optional[AdminResponse]:
        """Get current admin by username from token."""
        admin = await self.repo.get_by_username(db, username)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        return AdminResponse.model_validate(admin)

    async def create_admin(
        self,
        db: AsyncSession,
        data: AdminCreate
    ) -> AdminResponse:
        """Create a new admin."""
        # Check if username already exists
        existing = await self.repo.get_by_username(db, data.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Check if email already exists
        existing_email = await self.repo.get_by_email(db, data.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")

        # Hash password
        password_hash = hash_password(data.password)

        # Create admin
        admin = await self.repo.create(
            db,
            username=data.username,
            email=data.email,
            password_hash=password_hash,
            is_superadmin=data.is_superadmin
        )

        return AdminResponse.model_validate(admin)
