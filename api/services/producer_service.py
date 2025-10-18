"""Producer service for AI comment provider management."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import ProducerCreate, ProducerResponse
from core.security import encrypt_password
from core.instagram_helper import InstagramCommentBot
from api.repositories.producer_repository import ProducerRepository


class ProducerService:
    """Service for producer operations."""

    def __init__(self):
        self.repo = ProducerRepository()
        self.comment_bot = InstagramCommentBot()

    async def register_producer(
        self,
        db: AsyncSession,
        data: ProducerCreate
    ) -> ProducerResponse:
        """
        Register a new producer (user who provides account for AI comments).
        Verify Instagram login and save session.
        """
        # Check if Instagram ID already registered
        existing = await self.repo.get_by_instagram_id(db, data.instagram_id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Instagram ID already registered as producer"
            )

        # Attempt Instagram login
        try:
            # Encrypt password
            encrypted_password = encrypt_password(data.instagram_password)

            # Try to login
            success, session_data = self.comment_bot.login_with_password(
                data.instagram_id,
                encrypted_password,
                data.verification_code
            )

            if not success:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to login to Instagram. Please check credentials or provide verification code."
                )

            # Create producer record
            producer = await self.repo.create(
                db,
                instagram_id=data.instagram_id,
                instagram_password_encrypted=encrypted_password,
                session_data=session_data if session_data else None,
                verification_code=data.verification_code,
                is_active=True,
                is_verified=True  # Mark as verified after successful login
            )

            return ProducerResponse.model_validate(producer)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to register producer: {str(e)}"
            )

    async def get_all_producers(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProducerResponse]:
        """Get all producers."""
        producers = await self.repo.get_all(db, skip, limit)
        return [ProducerResponse.model_validate(p) for p in producers]

    async def get_active_producers(
        self,
        db: AsyncSession
    ) -> List[ProducerResponse]:
        """Get all active and verified producers."""
        producers = await self.repo.get_active_producers(db)
        return [ProducerResponse.model_validate(p) for p in producers]

    async def verify_producer(
        self,
        db: AsyncSession,
        producer_id: int
    ) -> ProducerResponse:
        """Mark producer as verified."""
        producer = await self.repo.verify_producer(db, producer_id)
        if not producer:
            raise HTTPException(status_code=404, detail="Producer not found")
        return ProducerResponse.model_validate(producer)
