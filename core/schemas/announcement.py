"""Pydantic schemas for announcement-related operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnnouncementCreate(BaseModel):
    """Announcement creation request."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    kakao_openchat_link: str | None = Field(None, max_length=500)
    kakao_qr_code_url: str | None = Field(None, max_length=500)
    is_active: bool = True


class AnnouncementUpdate(BaseModel):
    """Announcement update request."""
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)
    kakao_openchat_link: str | None = Field(None, max_length=500)
    kakao_qr_code_url: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class AnnouncementResponse(BaseModel):
    """Announcement response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    kakao_openchat_link: str | None
    kakao_qr_code_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
