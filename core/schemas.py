"""Pydantic schemas for API requests/responses."""
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


# SNS Raise User Schemas
class SnsRaiseUserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    instagram_id: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    is_active: bool = True


class SnsRaiseUserCreate(SnsRaiseUserBase):
    pass


class SnsRaiseUserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    instagram_id: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class SnsRaiseUserResponse(SnsRaiseUserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Request By Week Schemas
class RequestByWeekBase(BaseModel):
    instagram_link: str = Field(..., max_length=500)
    week_start_date: datetime
    week_end_date: datetime


class RequestByWeekCreate(RequestByWeekBase):
    user_id: int


class RequestByWeekResponse(RequestByWeekBase):
    id: int
    user_id: int
    request_date: datetime
    status: str
    comment_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# User Action Verification Schemas
class UserActionVerificationBase(BaseModel):
    instagram_link: str
    link_owner_username: str
    is_commented: bool = False


class UserActionVerificationCreate(UserActionVerificationBase):
    user_id: int
    request_id: int


class UserActionVerificationResponse(UserActionVerificationBase):
    id: int
    user_id: int
    request_id: int
    verified_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Helper Schemas
class HelperBase(BaseModel):
    instagram_id: str = Field(..., max_length=100)
    is_active: bool = True


class HelperCreate(BaseModel):
    instagram_id: str = Field(..., max_length=100)
    instagram_password: str
    verification_code: Optional[str] = None


class HelperResponse(HelperBase):
    id: int
    is_locked: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Consumer Schemas
class ConsumerBase(BaseModel):
    instagram_id: str = Field(..., max_length=100)
    comment_tone: Optional[str] = Field(None, max_length=50)
    special_requests: Optional[str] = None


class ConsumerCreate(ConsumerBase):
    pass


class ConsumerResponse(ConsumerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Producer Schemas
class ProducerCreate(BaseModel):
    instagram_id: str = Field(..., max_length=100)
    instagram_password: str
    verification_code: Optional[str] = None


class ProducerResponse(BaseModel):
    id: int
    instagram_id: str
    is_active: bool
    is_verified: bool
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Admin Schemas
class AdminBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class AdminCreate(AdminBase):
    password: str = Field(..., min_length=8)
    is_superadmin: bool = False


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminResponse(AdminBase):
    id: int
    is_active: bool
    is_superadmin: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Notice Schemas
class NoticeBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str
    is_pinned: bool = False
    is_important: bool = False


class NoticeCreate(NoticeBase):
    pass


class NoticeResponse(NoticeBase):
    id: int
    view_count: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Unfollow Checker
class UnfollowCheckerRequest(BaseModel):
    instagram_id: str
    instagram_password: str
    verification_code: Optional[str] = None


class UnfollowCheckerResponse(BaseModel):
    unfollowers: list[str]
    count: int


# Generic Response
class MessageResponse(BaseModel):
    message: str
    success: bool = True
