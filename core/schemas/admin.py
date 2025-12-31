"""Pydantic schemas for admin-related operations."""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AdminLogin(BaseModel):
    """Admin login request."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class AdminToken(BaseModel):
    """Admin authentication token response."""

    access_token: str
    token_type: str = "bearer"


class AdminCreate(BaseModel):
    """Admin creation request."""

    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8)


class AdminResponse(BaseModel):
    """Admin response model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime
