"""Notice service for announcement management."""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from core.schemas import NoticeCreate, NoticeResponse
from core.config import settings
from api.repositories.notice_repository import NoticeRepository


class NoticeService:
    """Service for notice operations."""

    def __init__(self):
        self.repo = NoticeRepository()

    async def get_all_notices(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> List[NoticeResponse]:
        """Get recent notices (pinned first)."""
        notices = await self.repo.get_recent_notices(db, limit)
        return [NoticeResponse.model_validate(n) for n in notices]

    async def get_notice_by_id(
        self,
        db: AsyncSession,
        notice_id: int
    ) -> NoticeResponse:
        """Get notice by ID and increment view count."""
        notice = await self.repo.get_by_id(db, notice_id)
        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")

        # Increment view count
        await self.repo.increment_view_count(db, notice_id)

        return NoticeResponse.model_validate(notice)

    async def create_notice(
        self,
        db: AsyncSession,
        data: NoticeCreate,
        author_id: int
    ) -> NoticeResponse:
        """Create a new notice."""
        notice = await self.repo.create(
            db,
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
            is_important=data.is_important,
            author_id=author_id,
            view_count=0
        )

        return NoticeResponse.model_validate(notice)

    async def update_notice(
        self,
        db: AsyncSession,
        notice_id: int,
        data: NoticeCreate
    ) -> NoticeResponse:
        """Update a notice."""
        notice = await self.repo.update(
            db,
            notice_id,
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
            is_important=data.is_important
        )

        if not notice:
            raise HTTPException(status_code=404, detail="Notice not found")

        return NoticeResponse.model_validate(notice)

    async def delete_notice(
        self,
        db: AsyncSession,
        notice_id: int
    ) -> dict:
        """Delete a notice."""
        success = await self.repo.delete(db, notice_id)

        if not success:
            raise HTTPException(status_code=404, detail="Notice not found")

        return {"message": "Notice deleted successfully", "success": True}

    async def get_notices_with_kakaotalk_info(
        self,
        db: AsyncSession,
        limit: int = 10
    ) -> dict:
        """Get notices along with KakaoTalk information."""
        notices = await self.get_all_notices(db, limit)

        return {
            "kakaotalk_open_chat_link": settings.KAKAOTALK_OPEN_CHAT_LINK,
            "kakaotalk_qr_code_path": settings.KAKAOTALK_QR_CODE_PATH,
            "notices": notices
        }
