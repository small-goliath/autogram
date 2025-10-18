"""Repository for user action verification operations."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from core.models import UserActionVerification
from api.repositories.base_repository import BaseRepository


class VerificationRepository(BaseRepository[UserActionVerification]):
    """Repository for user action verification operations."""

    def __init__(self):
        super().__init__(UserActionVerification)

    async def get_by_user_and_request(
        self,
        db: AsyncSession,
        user_id: int,
        request_id: int
    ) -> Optional[UserActionVerification]:
        """Get verification by user and request."""
        result = await db.execute(
            select(UserActionVerification).where(
                and_(
                    UserActionVerification.user_id == user_id,
                    UserActionVerification.request_id == request_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_unverified_actions(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserActionVerification]:
        """Get all unverified actions (not commented)."""
        result = await db.execute(
            select(UserActionVerification)
            .where(UserActionVerification.is_commented == False)
            .order_by(UserActionVerification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_username_filter(
        self,
        db: AsyncSession,
        username: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserActionVerification]:
        """Get verifications with optional username filter."""
        from core.models import SnsRaiseUser

        query = select(UserActionVerification).join(SnsRaiseUser)

        if username:
            query = query.where(SnsRaiseUser.username.ilike(f"%{username}%"))

        query = query.order_by(UserActionVerification.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    async def mark_as_commented(
        self,
        db: AsyncSession,
        id: int
    ) -> Optional[UserActionVerification]:
        """Mark verification as commented."""
        verification = await self.get_by_id(db, id)
        if not verification:
            return None

        verification.is_commented = True
        verification.verified_at = datetime.utcnow()
        await db.flush()
        await db.refresh(verification)
        return verification

    async def delete_by_user_and_request(
        self,
        db: AsyncSession,
        user_id: int,
        request_id: int
    ) -> bool:
        """Delete verification by user and request."""
        result = await db.execute(
            delete(UserActionVerification).where(
                and_(
                    UserActionVerification.user_id == user_id,
                    UserActionVerification.request_id == request_id
                )
            )
        )
        return result.rowcount > 0

    async def get_by_link_owner(
        self,
        db: AsyncSession,
        link_owner_username: str
    ) -> List[UserActionVerification]:
        """Get all verifications for a specific link owner."""
        result = await db.execute(
            select(UserActionVerification).where(
                UserActionVerification.link_owner_username == link_owner_username
            )
        )
        return list(result.scalars().all())
