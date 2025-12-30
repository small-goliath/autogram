"""Pydantic schemas for unfollower service user operations."""
from pydantic import BaseModel, Field


class UnfollowerServiceUserCreate(BaseModel):
    """Unfollower service user creation request."""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    totp_secret: str | None = Field(None, max_length=32, description="32-character TOTP secret (will be encrypted)")


class UnfollowerServiceUserResponse(BaseModel):
    """Unfollower service user response model."""
    username: str
    message: str
