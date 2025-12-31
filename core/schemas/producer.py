"""Pydantic schemas for producer-related operations."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProducerCreate(BaseModel):
    """Producer creation request."""

    instagram_username: str = Field(..., min_length=1, max_length=100)
    instagram_password: str = Field(..., min_length=1)
    totp_secret: str | None = Field(None, max_length=255)


class ProducerResponse(BaseModel):
    """Producer response model."""

    model_config = ConfigDict(from_attributes=True)

    instagram_username: str
    status: str
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime
