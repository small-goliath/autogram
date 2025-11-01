"""Pydantic schemas for helper-related operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class HelperCreate(BaseModel):
    """Helper account creation request."""
    instagram_username: str = Field(..., min_length=1, max_length=100)
    instagram_password: str = Field(..., min_length=1)
    verification_code: str | None = Field(None, max_length=50)


class HelperResponse(BaseModel):
    """Helper account response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    instagram_username: str
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime
