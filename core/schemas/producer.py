"""Pydantic schemas for producer-related operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProducerCreate(BaseModel):
    """Producer creation request."""
    instagram_username: str = Field(..., min_length=1, max_length=100)
    instagram_password: str = Field(..., min_length=1)
    verification_code: str | None = Field(None, max_length=50)


class ProducerResponse(BaseModel):
    """Producer response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    instagram_username: str
    status: str
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UnfollowCheckRequest(BaseModel):
    """Unfollow check request."""
    instagram_username: str = Field(..., min_length=1, max_length=100)
    instagram_password: str = Field(..., min_length=1)
    verification_code: str | None = Field(None, max_length=50)


class UnfollowCheckResponse(BaseModel):
    """Unfollow check response."""
    username: str
    unfollowers: list[str]
    unfollowers_count: int
