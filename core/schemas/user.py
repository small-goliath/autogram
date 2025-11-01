"""Pydantic schemas for SNS user-related operations."""
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict


class SnsUserCreate(BaseModel):
    """SNS user creation request."""
    username: str = Field(..., min_length=1, max_length=50)


class SnsUserUpdate(BaseModel):
    """SNS user update request."""
    username: str = Field(..., min_length=1, max_length=50)


class SnsUserResponse(BaseModel):
    """SNS user response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime
    updated_at: datetime


class RequestByWeekResponse(BaseModel):
    """Request by week response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    instagram_link: str
    week_start_date: date
    created_at: datetime


class UserActionVerificationResponse(BaseModel):
    """User action verification response model."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    instagram_link: str
    link_owner_username: str
    created_at: datetime
