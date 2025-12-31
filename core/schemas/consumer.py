"""Pydantic schemas for consumer-related operations."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ConsumerCreate(BaseModel):
    """Consumer creation request."""
    instagram_username: str = Field(..., min_length=1, max_length=100)


class ConsumerResponse(BaseModel):
    """Consumer response model."""
    model_config = ConfigDict(from_attributes=True)

    instagram_username: str
    status: str
    created_at: datetime
    updated_at: datetime
