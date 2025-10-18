# Autogram FastAPI Backend Architecture

## Table of Contents
1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Database Architecture](#database-architecture)
4. [Service Layer Architecture](#service-layer-architecture)
5. [API Layer Architecture](#api-layer-architecture)
6. [Authentication & Authorization](#authentication--authorization)
7. [Error Handling Strategy](#error-handling-strategy)
8. [Configuration Management](#configuration-management)
9. [Instagram Integration Strategy](#instagram-integration-strategy)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

Autogram is an Instagram comment exchange service built with:
- **FastAPI** (Python 3.13) for the backend API
- **Next.js 14** for the frontend
- **SQLAlchemy 2.0** with async support for database operations
- **Instaloader** for Instagram read-only operations
- **Instagrapi** for Instagram comment writing operations
- **PostgreSQL** as the primary database

### Architecture Principles
1. **Separation of Concerns**: Business logic in services, data access in DB layer
2. **Dependency Injection**: Leveraging FastAPI's DI system
3. **Type Safety**: Comprehensive Pydantic models and type hints
4. **Async-First**: All database and Instagram operations are async
5. **Modular Design**: Clear separation between public and admin APIs
6. **Security**: JWT-based admin authentication with proper validation

---

## Directory Structure

```
/Users/iymaeng/Documents/private/autogram-latest/
├── api/                                # FastAPI Backend
│   ├── __init__.py
│   ├── index.py                        # Main FastAPI app entry point
│   ├── config.py                       # Configuration management
│   ├── dependencies.py                 # Shared dependencies (DB, auth, etc.)
│   │
│   ├── core/                           # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py                 # JWT, password hashing, auth utilities
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── logging.py                  # Logging configuration
│   │   └── middleware.py               # Custom middleware (CORS, error handling)
│   │
│   ├── db/                             # Database layer
│   │   ├── __init__.py
│   │   ├── session.py                  # Database session management
│   │   ├── base.py                     # Base class for all models
│   │   ├── models/                     # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── sns_raise_user.py      # SnsRaiseUser model
│   │   │   ├── request_by_week.py     # RequestByWeek model
│   │   │   ├── user_action_verification.py  # UserActionVerification model
│   │   │   ├── helper.py              # Helper model
│   │   │   ├── consumer.py            # Consumer model
│   │   │   ├── producer.py            # Producer model
│   │   │   └── admin.py               # Admin model
│   │   │
│   │   └── repositories/               # Database access layer (*_db.py pattern)
│   │       ├── __init__.py
│   │       ├── sns_raise_user_db.py
│   │       ├── request_by_week_db.py
│   │       ├── user_action_verification_db.py
│   │       ├── helper_db.py
│   │       ├── consumer_db.py
│   │       ├── producer_db.py
│   │       ├── admin_db.py
│   │       └── notice_db.py
│   │
│   ├── schemas/                        # Pydantic models
│   │   ├── __init__.py
│   │   ├── common.py                   # Common schemas (responses, pagination)
│   │   ├── sns_raise_user.py
│   │   ├── request_by_week.py
│   │   ├── user_action_verification.py
│   │   ├── helper.py
│   │   ├── consumer.py
│   │   ├── producer.py
│   │   ├── admin.py
│   │   ├── notice.py
│   │   └── auth.py                     # Authentication schemas
│   │
│   ├── services/                       # Business logic layer (*_service.py pattern)
│   │   ├── __init__.py
│   │   ├── sns_raise_user_service.py
│   │   ├── request_by_week_service.py
│   │   ├── user_action_verification_service.py
│   │   ├── helper_service.py
│   │   ├── consumer_service.py
│   │   ├── producer_service.py
│   │   ├── notice_service.py
│   │   ├── unfollow_checker_service.py
│   │   ├── instagram_service.py        # Instagram integration wrapper
│   │   └── auth_service.py             # Authentication business logic
│   │
│   ├── integrations/                   # External service integrations
│   │   ├── __init__.py
│   │   ├── instaloader_client.py       # Instaloader wrapper
│   │   └── instagrapi_client.py        # Instagrapi wrapper
│   │
│   └── routers/                        # API route handlers
│       ├── __init__.py
│       ├── public/                     # Public API routes
│       │   ├── __init__.py
│       │   ├── notices.py
│       │   ├── requests_by_week.py
│       │   ├── user_action_verification.py
│       │   ├── consumer.py
│       │   ├── producer.py
│       │   └── unfollow_checker.py
│       │
│       └── admin/                      # Admin API routes (auth required)
│           ├── __init__.py
│           ├── auth.py                 # Admin login/logout
│           ├── sns_users.py
│           └── helpers.py
│
├── batch/                              # Batch processing jobs
│   ├── __init__.py
│   ├── weekly_verification_check.py    # Weekly verification job
│   └── ai_comment_generator.py         # AI comment generation job
│
├── core/                               # Shared logic between api and batch
│   ├── __init__.py
│   ├── constants.py                    # Shared constants
│   └── utils.py                        # Shared utility functions
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── test_api/
│   │   ├── test_public/
│   │   └── test_admin/
│   ├── test_services/
│   └── test_repositories/
│
├── alembic/                            # Database migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt                    # Python dependencies
├── pyproject.toml                      # Python project configuration
├── alembic.ini                         # Alembic configuration
└── .env.example                        # Environment variables template
```

---

## Database Architecture

### Entity Relationship Diagram

```
┌─────────────────────┐
│   sns_raise_user    │
│ ─────────────────── │
│ id (PK)            │
│ username (unique)   │
│ created_at         │
│ updated_at         │
└──────────┬──────────┘
           │ 1
           │
           │ *
┌──────────┴──────────┐         ┌─────────────────────────┐
│  request_by_week    │         │ user_action_verification│
│ ─────────────────── │         │ ───────────────────────│
│ id (PK)            │         │ id (PK)                │
│ user_id (FK)       │         │ user_id (FK)           │
│ week_number        │         │ request_id (FK)        │
│ year               │         │ is_verified            │
│ instagram_link     │         │ verified_at            │
│ created_at         │         │ created_at             │
└────────────────────┘         └─────────────────────────┘
                                            │
                                            │ *
                                            │
                                            │ 1
                                 ┌──────────┴──────────┐
                                 │  request_by_week    │
                                 └─────────────────────┘

┌─────────────────────┐
│      helper         │
│ ─────────────────── │
│ id (PK)            │
│ instagram_id       │
│ password (encrypted)│
│ session_data (JSON) │
│ is_active          │
│ last_used_at       │
│ created_at         │
└─────────────────────┘

┌─────────────────────┐         ┌─────────────────────┐
│     consumer        │         │      producer       │
│ ─────────────────── │         │ ─────────────────── │
│ id (PK)            │         │ id (PK)            │
│ instagram_id       │         │ instagram_id       │
│ is_active          │         │ password (encrypted)│
│ created_at         │         │ verification_code   │
│ updated_at         │         │ is_verified        │
└─────────────────────┘         │ is_active          │
                                │ session_data (JSON) │
                                │ created_at         │
                                │ updated_at         │
                                └─────────────────────┘

┌─────────────────────┐
│       admin         │
│ ─────────────────── │
│ id (PK)            │
│ username (unique)   │
│ password_hash      │
│ is_active          │
│ last_login_at      │
│ created_at         │
└─────────────────────┘
```

### Model Specifications

#### 1. SnsRaiseUser Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/sns_raise_user.py

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from api.db.base import Base

class SnsRaiseUser(Base):
    __tablename__ = "sns_raise_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    requests = relationship(
        "RequestByWeek",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    verifications = relationship(
        "UserActionVerification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
```

#### 2. RequestByWeek Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/request_by_week.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from api.db.base import Base

class RequestByWeek(Base):
    __tablename__ = "request_by_week"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("sns_raise_user.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)  # ISO week number (1-53)
    year = Column(Integer, nullable=False)  # Year
    instagram_link = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("SnsRaiseUser", back_populates="requests")
    verifications = relationship(
        "UserActionVerification",
        back_populates="request",
        cascade="all, delete-orphan"
    )

    # Composite index for efficient week-based queries
    __table_args__ = (
        Index('idx_week_year', 'week_number', 'year'),
        Index('idx_user_week_year', 'user_id', 'week_number', 'year'),
    )
```

#### 3. UserActionVerification Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/user_action_verification.py

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from api.db.base import Base

class UserActionVerification(Base):
    __tablename__ = "user_action_verification"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("sns_raise_user.id", ondelete="CASCADE"), nullable=False)
    request_id = Column(Integer, ForeignKey("request_by_week.id", ondelete="CASCADE"), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("SnsRaiseUser", back_populates="verifications")
    request = relationship("RequestByWeek", back_populates="verifications")

    # Ensure one verification record per user per request
    __table_args__ = (
        Index('idx_user_request', 'user_id', 'request_id', unique=True),
        Index('idx_unverified', 'is_verified', 'user_id'),
    )
```

#### 4. Helper Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/helper.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, func
from api.db.base import Base

class Helper(Base):
    __tablename__ = "helper"

    id = Column(Integer, primary_key=True, index=True)
    instagram_id = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(500), nullable=False)  # Encrypted
    session_data = Column(JSON, nullable=True)  # Stores Instaloader session
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 5. Consumer Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/consumer.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from api.db.base import Base

class Consumer(Base):
    __tablename__ = "consumer"

    id = Column(Integer, primary_key=True, index=True)
    instagram_id = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 6. Producer Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/producer.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, func
from api.db.base import Base

class Producer(Base):
    __tablename__ = "producer"

    id = Column(Integer, primary_key=True, index=True)
    instagram_id = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(500), nullable=False)  # Encrypted
    verification_code = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    session_data = Column(JSON, nullable=True)  # Stores Instagrapi session
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 7. Admin Model
```python
# Location: /Users/iymaeng/Documents/private/autogram-latest/api/db/models/admin.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from api.db.base import Base

class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## Service Layer Architecture

The service layer contains all business logic. Each service follows the `*_service.py` naming pattern.

### Service Layer Principles
1. Services orchestrate business logic and coordinate between repositories
2. Services handle validation, transformation, and business rules
3. Services are injected into routers via dependency injection
4. Services do NOT directly access SQLAlchemy models (use repositories)
5. Services work with Pydantic schemas for type safety

### Service Structure Template

```python
# Example: /Users/iymaeng/Documents/private/autogram-latest/api/services/sns_raise_user_service.py

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.repositories.sns_raise_user_db import SnsRaiseUserRepository
from api.schemas.sns_raise_user import SnsRaiseUserCreate, SnsRaiseUserUpdate, SnsRaiseUserResponse
from api.core.exceptions import NotFoundException, DuplicateException

class SnsRaiseUserService:
    """Business logic for SNS Raise User operations"""

    def __init__(self, db: AsyncSession):
        self.repository = SnsRaiseUserRepository(db)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[SnsRaiseUserResponse]:
        """Get all users with pagination"""
        users = await self.repository.get_all(skip=skip, limit=limit)
        return [SnsRaiseUserResponse.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> SnsRaiseUserResponse:
        """Get user by ID"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return SnsRaiseUserResponse.model_validate(user)

    async def create_user(self, user_data: SnsRaiseUserCreate) -> SnsRaiseUserResponse:
        """Create a new user"""
        # Check for duplicates
        existing_user = await self.repository.get_by_username(user_data.username)
        if existing_user:
            raise DuplicateException(f"User with username {user_data.username} already exists")

        user = await self.repository.create(user_data)
        return SnsRaiseUserResponse.model_validate(user)

    async def update_user(self, user_id: int, user_data: SnsRaiseUserUpdate) -> SnsRaiseUserResponse:
        """Update an existing user"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        # Check for username conflicts if username is being updated
        if user_data.username and user_data.username != user.username:
            existing_user = await self.repository.get_by_username(user_data.username)
            if existing_user:
                raise DuplicateException(f"User with username {user_data.username} already exists")

        updated_user = await self.repository.update(user_id, user_data)
        return SnsRaiseUserResponse.model_validate(updated_user)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user (cascade deletes related data)"""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        return await self.repository.delete(user_id)
```

### Key Services

#### 1. SNS Raise User Service
- `get_all_users()` - List all users with pagination
- `get_user_by_id()` - Get specific user
- `get_user_by_username()` - Get user by username
- `create_user()` - Create new user with validation
- `update_user()` - Update user with conflict checking
- `delete_user()` - Delete user with cascade

#### 2. Request By Week Service
- `get_requests_by_week()` - Get all requests for a specific week/year
- `get_requests_by_username()` - Filter requests by username
- `create_request()` - Create weekly request with validation
- `get_user_requests()` - Get all requests for a specific user

#### 3. User Action Verification Service
- `get_verifications()` - Get all verifications (filterable by username)
- `get_unverified_actions()` - Get pending verifications
- `mark_as_verified()` - Mark action as verified
- `get_user_pending_verifications()` - Get pending verifications for a user

#### 4. Helper Service
- `get_all_helpers()` - List all helper accounts
- `get_active_helper()` - Get an available active helper account
- `create_helper()` - Register new helper with Instaloader login
- `update_session()` - Update helper session data
- `delete_helper()` - Remove helper account
- `rotate_helper()` - Mark helper as used and get next available

#### 5. Consumer Service
- `register_consumer()` - Register Instagram ID for AI auto-comments
- `get_active_consumers()` - Get all active consumers
- `deactivate_consumer()` - Deactivate a consumer

#### 6. Producer Service
- `register_producer()` - Register producer with verification code
- `verify_producer()` - Verify producer account
- `get_active_producers()` - Get all verified active producers
- `update_session()` - Update producer session data

#### 7. Unfollow Checker Service
- `check_unfollowers()` - Compare followers/following and find unfollowers
- `verify_instagram_credentials()` - Verify user credentials
- `get_follower_stats()` - Get follower/following counts

#### 8. Instagram Service
- `login_with_instaloader()` - Login and save session (read-only)
- `login_with_instagrapi()` - Login for writing operations
- `load_session()` - Load saved session
- `get_post_info()` - Get post information
- `write_comment()` - Write comment to post
- `get_followers()` - Get follower list
- `get_following()` - Get following list

#### 9. Notice Service
- `get_notices()` - Get announcement information (KakaoTalk link, QR, notices)
- `update_notices()` - Update notice information (admin only)

#### 10. Auth Service
- `authenticate_admin()` - Verify admin credentials
- `create_access_token()` - Generate JWT token
- `verify_token()` - Verify and decode JWT token
- `get_current_admin()` - Get admin from token

---

## API Layer Architecture

### Router Organization

#### Public Routes (No Authentication Required)

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/__init__.py

from fastapi import APIRouter
from api.routers.public import (
    notices,
    requests_by_week,
    user_action_verification,
    consumer,
    producer,
    unfollow_checker
)

public_router = APIRouter(prefix="/api", tags=["public"])

public_router.include_router(notices.router)
public_router.include_router(requests_by_week.router)
public_router.include_router(user_action_verification.router)
public_router.include_router(consumer.router)
public_router.include_router(producer.router)
public_router.include_router(unfollow_checker.router)
```

##### 1. Notices Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/notices.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.notice_service import NoticeService
from api.schemas.notice import NoticeResponse

router = APIRouter(prefix="/notices", tags=["notices"])

@router.get("", response_model=NoticeResponse)
async def get_notices(
    db: AsyncSession = Depends(get_db)
):
    """Get announcement information (KakaoTalk link, QR code, notices)"""
    service = NoticeService(db)
    return await service.get_notices()
```

##### 2. Requests By Week Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/requests_by_week.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.request_by_week_service import RequestByWeekService
from api.schemas.request_by_week import RequestByWeekResponse
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/requests-by-week", tags=["requests"])

@router.get("", response_model=PaginatedResponse[RequestByWeekResponse])
async def get_requests_by_week(
    username: Optional[str] = Query(None, description="Filter by username"),
    week_number: Optional[int] = Query(None, ge=1, le=53),
    year: Optional[int] = Query(None, ge=2020),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get weekly request data with optional filtering"""
    service = RequestByWeekService(db)
    return await service.get_requests(
        username=username,
        week_number=week_number,
        year=year,
        skip=skip,
        limit=limit
    )
```

##### 3. User Action Verification Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/user_action_verification.py

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.user_action_verification_service import UserActionVerificationService
from api.schemas.user_action_verification import UserActionVerificationResponse
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/user-action-verification", tags=["verification"])

@router.get("", response_model=PaginatedResponse[UserActionVerificationResponse])
async def get_user_action_verifications(
    username: Optional[str] = Query(None, description="Filter by username"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get verification data with optional filtering"""
    service = UserActionVerificationService(db)
    return await service.get_verifications(
        username=username,
        is_verified=is_verified,
        skip=skip,
        limit=limit
    )
```

##### 4. Consumer Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/consumer.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.consumer_service import ConsumerService
from api.schemas.consumer import ConsumerCreate, ConsumerResponse

router = APIRouter(prefix="/consumer", tags=["consumer"])

@router.post("", response_model=ConsumerResponse, status_code=status.HTTP_201_CREATED)
async def register_consumer(
    consumer_data: ConsumerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register for AI auto-comment receiving"""
    service = ConsumerService(db)
    return await service.register_consumer(consumer_data)
```

##### 5. Producer Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/producer.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.producer_service import ProducerService
from api.schemas.producer import ProducerCreate, ProducerResponse

router = APIRouter(prefix="/producer", tags=["producer"])

@router.post("", response_model=ProducerResponse, status_code=status.HTTP_201_CREATED)
async def register_producer(
    producer_data: ProducerCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register for AI auto-comment providing with verification"""
    service = ProducerService(db)
    return await service.register_producer(producer_data)
```

##### 6. Unfollow Checker Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/public/unfollow_checker.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.unfollow_checker_service import UnfollowCheckerService
from api.schemas.unfollow_checker import UnfollowCheckRequest, UnfollowCheckResponse

router = APIRouter(prefix="/unfollow-checker", tags=["unfollow"])

@router.post("", response_model=UnfollowCheckResponse)
async def check_unfollowers(
    request_data: UnfollowCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """Check who unfollowed you"""
    service = UnfollowCheckerService(db)
    return await service.check_unfollowers(request_data)
```

#### Admin Routes (JWT Authentication Required)

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/admin/__init__.py

from fastapi import APIRouter
from api.routers.admin import auth, sns_users, helpers

admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

admin_router.include_router(auth.router)
admin_router.include_router(sns_users.router)
admin_router.include_router(helpers.router)
```

##### 1. Admin Auth Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/admin/auth.py

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db
from api.services.auth_service import AuthService
from api.schemas.auth import Token, AdminResponse

router = APIRouter(tags=["auth"])

@router.post("/login", response_model=Token)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Admin login - returns JWT access token"""
    service = AuthService(db)
    return await service.authenticate_admin(form_data.username, form_data.password)

@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: AdminResponse = Depends(get_current_admin)
):
    """Get current admin information"""
    return current_admin
```

##### 2. SNS Users Admin Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/admin/sns_users.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_admin
from api.services.sns_raise_user_service import SnsRaiseUserService
from api.schemas.sns_raise_user import (
    SnsRaiseUserCreate,
    SnsRaiseUserUpdate,
    SnsRaiseUserResponse
)
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/sns-users", tags=["sns-users"])

@router.get("", response_model=PaginatedResponse[SnsRaiseUserResponse])
async def list_sns_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """List all SNS raise users"""
    service = SnsRaiseUserService(db)
    return await service.get_all_users(skip=skip, limit=limit)

@router.post("", response_model=SnsRaiseUserResponse, status_code=status.HTTP_201_CREATED)
async def create_sns_user(
    user_data: SnsRaiseUserCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Create a new SNS raise user"""
    service = SnsRaiseUserService(db)
    return await service.create_user(user_data)

@router.put("/{user_id}", response_model=SnsRaiseUserResponse)
async def update_sns_user(
    user_id: int,
    user_data: SnsRaiseUserUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Update an SNS raise user"""
    service = SnsRaiseUserService(db)
    return await service.update_user(user_id, user_data)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sns_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete an SNS raise user (cascade deletes related data)"""
    service = SnsRaiseUserService(db)
    await service.delete_user(user_id)
```

##### 3. Helpers Admin Router
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/routers/admin/helpers.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_admin
from api.services.helper_service import HelperService
from api.schemas.helper import HelperCreate, HelperResponse
from api.schemas.common import PaginatedResponse

router = APIRouter(prefix="/helpers", tags=["helpers"])

@router.get("", response_model=PaginatedResponse[HelperResponse])
async def list_helpers(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """List all helper accounts"""
    service = HelperService(db)
    return await service.get_all_helpers(skip=skip, limit=limit)

@router.post("", response_model=HelperResponse, status_code=status.HTTP_201_CREATED)
async def create_helper(
    helper_data: HelperCreate,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Register a new helper account (logs in with Instaloader and saves session)"""
    service = HelperService(db)
    return await service.create_helper(helper_data)

@router.delete("/{helper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_helper(
    helper_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """Delete a helper account"""
    service = HelperService(db)
    await service.delete_helper(helper_id)
```

---

## Authentication & Authorization

### JWT-Based Authentication Strategy

#### Overview
- Admin routes require JWT (JSON Web Token) authentication
- Public routes do not require authentication
- JWT tokens are issued upon successful admin login
- Tokens contain admin ID and expiration time
- Tokens must be included in the `Authorization` header as `Bearer <token>`

#### Implementation

##### 1. Security Utilities
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/core/security.py

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from api.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

# JWT token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# Instagram credential encryption (for storing helper/producer passwords)
from cryptography.fernet import Fernet

def encrypt_password(password: str) -> str:
    """Encrypt Instagram password for storage"""
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decrypt Instagram password from storage"""
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.decrypt(encrypted_password.encode()).decode()
```

##### 2. Authentication Dependencies
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/dependencies.py

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.session import get_session
from api.core.security import verify_token
from api.db.repositories.admin_db import AdminRepository
from api.schemas.admin import AdminResponse

# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async for session in get_session():
        yield session

# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> AdminResponse:
    """Get current authenticated admin from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    admin_id: int = payload.get("sub")
    if admin_id is None:
        raise credentials_exception

    # Get admin from database
    admin_repo = AdminRepository(db)
    admin = await admin_repo.get_by_id(admin_id)

    if admin is None or not admin.is_active:
        raise credentials_exception

    return AdminResponse.model_validate(admin)
```

##### 3. Auth Service
```python
# /Users/iymaeng/Documents/private/autogram-latest/api/services/auth_service.py

from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.repositories.admin_db import AdminRepository
from api.core.security import verify_password, create_access_token
from api.schemas.auth import Token
from api.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.admin_repo = AdminRepository(db)

    async def authenticate_admin(self, username: str, password: str) -> Token:
        """Authenticate admin and return JWT token"""
        admin = await self.admin_repo.get_by_username(username)

        if not admin or not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        if not verify_password(password, admin.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )

        # Update last login time
        await self.admin_repo.update_last_login(admin.id)

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(admin.id)},
            expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")
```

### Security Considerations

1. **Password Storage**:
   - Admin passwords: bcrypt hashing (one-way)
   - Instagram passwords (helper/producer): Fernet symmetric encryption (reversible)

2. **Token Management**:
   - JWT tokens expire after configured time (default: 30 minutes)
   - Tokens include admin ID in the `sub` claim
   - Token verification on every admin endpoint request

3. **Instagram Credentials**:
   - Helper account passwords are encrypted before storage
   - Producer account passwords are encrypted before storage
   - Session data is stored as JSON in the database

4. **Rate Limiting** (recommended for production):
   - Implement rate limiting on login endpoint
   - Implement rate limiting on Instagram operations
   - Use Redis or similar for distributed rate limiting

---

## Error Handling Strategy

### Custom Exception Classes

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/core/exceptions.py

from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """Raised when a resource is not found"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class DuplicateException(HTTPException):
    """Raised when trying to create a duplicate resource"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class BadRequestException(HTTPException):
    """Raised for invalid request data"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnauthorizedException(HTTPException):
    """Raised for authentication failures"""
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class ForbiddenException(HTTPException):
    """Raised for authorization failures"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class InstagramException(HTTPException):
    """Raised for Instagram API errors"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Instagram service error: {detail}"
        )

class ValidationException(HTTPException):
    """Raised for business logic validation errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
```

### Global Exception Handlers

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/core/middleware.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "message": "An internal error occurred. Please try again later."
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )
```

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Detailed error message or validation errors array",
  "message": "Human-readable error message (optional)"
}
```

---

## Configuration Management

### Configuration Structure

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/config.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Autogram API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str  # For encrypting Instagram passwords (Fernet key)

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # Instagram
    INSTALOADER_SESSION_DIR: str = "/tmp/instaloader_sessions"
    INSTAGRAPI_SESSION_DIR: str = "/tmp/instagrapi_sessions"
    INSTAGRAM_REQUEST_DELAY: float = 2.0  # Seconds between requests

    # Pagination
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 500

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

settings = get_settings()
```

### Environment Variables (.env.example)

```bash
# /Users/iymaeng/Documents/private/autogram-latest/.env.example

# Application
APP_NAME=Autogram API
DEBUG=False

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/autogram

# Security
SECRET_KEY=your-secret-key-here-minimum-32-characters
ENCRYPTION_KEY=your-fernet-encryption-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (comma-separated for multiple origins)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Instagram
INSTALOADER_SESSION_DIR=/tmp/instaloader_sessions
INSTAGRAPI_SESSION_DIR=/tmp/instagrapi_sessions
INSTAGRAM_REQUEST_DELAY=2.0

# Logging
LOG_LEVEL=INFO
```

---

## Instagram Integration Strategy

### Overview

The system uses two Instagram libraries:
1. **Instaloader**: Read-only operations (viewing posts, followers, following)
2. **Instagrapi**: Write operations (commenting on posts)

### Integration Architecture

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/integrations/instaloader_client.py

import asyncio
from typing import Optional, Dict, Any
import instaloader
from pathlib import Path
from api.config import settings
from api.core.exceptions import InstagramException

class InstaloaderClient:
    """Wrapper for Instaloader (read-only Instagram operations)"""

    def __init__(self):
        self.loader = instaloader.Instaloader(
            dirname_pattern=settings.INSTALOADER_SESSION_DIR,
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and return session data"""
        try:
            # Run blocking Instaloader operation in thread pool
            await asyncio.to_thread(self.loader.login, username, password)

            # Save session
            session_file = Path(settings.INSTALOADER_SESSION_DIR) / f"session-{username}"
            await asyncio.to_thread(self.loader.save_session_to_file, session_file)

            # Return session data
            return {
                "username": username,
                "session_file": str(session_file),
                "cookies": dict(self.loader.context._session.cookies)
            }
        except Exception as e:
            raise InstagramException(f"Failed to login: {str(e)}")

    async def load_session(self, session_data: Dict[str, Any]) -> None:
        """Load existing session"""
        try:
            username = session_data["username"]
            session_file = Path(session_data["session_file"])

            if session_file.exists():
                await asyncio.to_thread(self.loader.load_session_from_file, username, session_file)
            else:
                raise InstagramException("Session file not found")
        except Exception as e:
            raise InstagramException(f"Failed to load session: {str(e)}")

    async def get_profile(self, username: str) -> instaloader.Profile:
        """Get user profile"""
        try:
            profile = await asyncio.to_thread(
                instaloader.Profile.from_username,
                self.loader.context,
                username
            )
            return profile
        except Exception as e:
            raise InstagramException(f"Failed to get profile: {str(e)}")

    async def get_followers(self, username: str) -> list[str]:
        """Get list of followers"""
        try:
            profile = await self.get_profile(username)
            followers = await asyncio.to_thread(
                lambda: list(profile.get_followers())
            )
            return [f.username for f in followers]
        except Exception as e:
            raise InstagramException(f"Failed to get followers: {str(e)}")

    async def get_following(self, username: str) -> list[str]:
        """Get list of following"""
        try:
            profile = await self.get_profile(username)
            following = await asyncio.to_thread(
                lambda: list(profile.get_followees())
            )
            return [f.username for f in following]
        except Exception as e:
            raise InstagramException(f"Failed to get following: {str(e)}")

    async def get_post_info(self, shortcode: str) -> Dict[str, Any]:
        """Get post information by shortcode"""
        try:
            post = await asyncio.to_thread(
                instaloader.Post.from_shortcode,
                self.loader.context,
                shortcode
            )
            return {
                "shortcode": post.shortcode,
                "owner": post.owner_username,
                "caption": post.caption,
                "likes": post.likes,
                "comments": post.comments,
                "date": post.date_utc
            }
        except Exception as e:
            raise InstagramException(f"Failed to get post info: {str(e)}")
```

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/integrations/instagrapi_client.py

import asyncio
from typing import Optional, Dict, Any
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes
from pathlib import Path
from api.config import settings
from api.core.exceptions import InstagramException

class InstagrapiClient:
    """Wrapper for Instagrapi (write Instagram operations)"""

    def __init__(self):
        self.client = Client()
        self.client.delay_range = [1, 3]

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and return session data"""
        try:
            # Run blocking operation in thread pool
            await asyncio.to_thread(self.client.login, username, password)

            # Save session
            session_file = Path(settings.INSTAGRAPI_SESSION_DIR) / f"session-{username}.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            await asyncio.to_thread(self.client.dump_settings, session_file)

            # Return session data
            return {
                "username": username,
                "session_file": str(session_file),
                "settings": self.client.get_settings()
            }
        except PleaseWaitFewMinutes:
            raise InstagramException("Rate limited. Please wait a few minutes.")
        except Exception as e:
            raise InstagramException(f"Failed to login: {str(e)}")

    async def load_session(self, session_data: Dict[str, Any]) -> None:
        """Load existing session"""
        try:
            session_file = Path(session_data["session_file"])

            if session_file.exists():
                await asyncio.to_thread(self.client.load_settings, session_file)
                await asyncio.to_thread(self.client.login, session_data["username"], "")
            else:
                raise InstagramException("Session file not found")
        except LoginRequired:
            raise InstagramException("Session expired. Please re-login.")
        except Exception as e:
            raise InstagramException(f"Failed to load session: {str(e)}")

    async def comment_post(self, post_id: str, text: str) -> Dict[str, Any]:
        """Post a comment on an Instagram post"""
        try:
            # Add delay to avoid rate limiting
            await asyncio.sleep(settings.INSTAGRAM_REQUEST_DELAY)

            # Post comment
            comment = await asyncio.to_thread(
                self.client.media_comment,
                post_id,
                text
            )

            return {
                "comment_id": comment.pk,
                "text": comment.text,
                "created_at": comment.created_at_utc
            }
        except PleaseWaitFewMinutes:
            raise InstagramException("Rate limited. Please wait before commenting again.")
        except Exception as e:
            raise InstagramException(f"Failed to post comment: {str(e)}")

    async def verify_credentials(self, username: str, password: str) -> bool:
        """Verify Instagram credentials without saving session"""
        try:
            temp_client = Client()
            await asyncio.to_thread(temp_client.login, username, password)
            await asyncio.to_thread(temp_client.logout)
            return True
        except Exception:
            return False
```

### Instagram Service Layer

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/services/instagram_service.py

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from api.integrations.instaloader_client import InstaloaderClient
from api.integrations.instagrapi_client import InstagrapiClient
from api.db.repositories.helper_db import HelperRepository
from api.core.exceptions import InstagramException
from api.core.security import encrypt_password, decrypt_password

class InstagramService:
    """High-level Instagram operations service"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.helper_repo = HelperRepository(db)
        self.instaloader = InstaloaderClient()
        self.instagrapi = InstagrapiClient()

    async def get_helper_client(self) -> InstaloaderClient:
        """Get an authenticated Instaloader client using a helper account"""
        # Get an available helper account
        helper = await self.helper_repo.get_active_helper()

        if not helper:
            raise InstagramException("No helper accounts available")

        # Load session
        if helper.session_data:
            await self.instaloader.load_session(helper.session_data)
        else:
            # Login and save session
            password = decrypt_password(helper.password)
            session_data = await self.instaloader.login(helper.instagram_id, password)
            await self.helper_repo.update_session(helper.id, session_data)

        # Update last used time
        await self.helper_repo.update_last_used(helper.id)

        return self.instaloader

    async def login_producer(self, instagram_id: str, password: str) -> Dict[str, Any]:
        """Login a producer account and return session data"""
        encrypted_password = encrypt_password(password)
        session_data = await self.instagrapi.login(instagram_id, password)
        return {
            "encrypted_password": encrypted_password,
            "session_data": session_data
        }

    async def load_producer_session(self, session_data: Dict[str, Any]) -> InstagrapiClient:
        """Load producer session and return authenticated client"""
        await self.instagrapi.load_session(session_data)
        return self.instagrapi

    async def check_unfollowers(self, username: str, password: str) -> Dict[str, Any]:
        """Check who unfollowed the user"""
        # Login with Instaloader
        await self.instaloader.login(username, password)

        # Get followers and following
        followers = await self.instaloader.get_followers(username)
        following = await self.instaloader.get_following(username)

        # Calculate unfollowers (people you follow but don't follow you back)
        followers_set = set(followers)
        following_set = set(following)
        unfollowers = following_set - followers_set

        return {
            "followers_count": len(followers),
            "following_count": len(following),
            "unfollowers_count": len(unfollowers),
            "unfollowers": list(unfollowers)
        }
```

### Session Management Strategy

1. **Helper Accounts**:
   - Sessions are saved in database after first login
   - Sessions are reused for subsequent operations
   - Helper accounts are rotated to avoid rate limiting
   - `last_used_at` timestamp tracks usage

2. **Producer Accounts**:
   - Sessions are saved after verification
   - Sessions are loaded for AI comment operations
   - Failed sessions trigger re-authentication

3. **Session Storage**:
   - Instaloader: Session files + cookie data in JSON
   - Instagrapi: Settings JSON blob
   - Both stored in database `session_data` JSON column

---

## Database Layer Architecture

### Repository Pattern

Each table has a corresponding repository class in the `*_db.py` pattern.

### Base Repository

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/db/repositories/base.py

from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Get all entities with pagination"""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> ModelType:
        """Create new entity"""
        entity = self.model(**data)
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def update(self, id: int, data: dict) -> Optional[ModelType]:
        """Update entity"""
        await self.db.execute(
            update(self.model).where(self.model.id == id).values(**data)
        )
        await self.db.commit()
        return await self.get_by_id(id)

    async def delete(self, id: int) -> bool:
        """Delete entity"""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
```

### Example Repository Implementation

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/db/repositories/sns_raise_user_db.py

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.models.sns_raise_user import SnsRaiseUser
from api.db.repositories.base import BaseRepository

class SnsRaiseUserRepository(BaseRepository[SnsRaiseUser]):
    """Repository for SNS Raise User database operations"""

    def __init__(self, db: AsyncSession):
        super().__init__(SnsRaiseUser, db)

    async def get_by_username(self, username: str) -> Optional[SnsRaiseUser]:
        """Get user by username"""
        result = await self.db.execute(
            select(SnsRaiseUser).where(SnsRaiseUser.username == username)
        )
        return result.scalar_one_or_none()

    async def exists_by_username(self, username: str) -> bool:
        """Check if username exists"""
        user = await self.get_by_username(username)
        return user is not None
```

### Database Session Management

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from api.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Base Model

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/db/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass
```

---

## Implementation Roadmap

### Phase 1: Project Setup (Week 1)
1. Set up directory structure
2. Configure dependencies (requirements.txt)
3. Set up database connection and Alembic
4. Create base models and repositories
5. Configure logging and middleware

### Phase 2: Core Infrastructure (Week 2)
1. Implement authentication system
2. Create custom exceptions and error handlers
3. Set up Instagram integration clients
4. Implement configuration management
5. Create database migrations

### Phase 3: Admin APIs (Week 3)
1. Implement SNS users CRUD operations
2. Implement helper account management
3. Add admin authentication endpoints
4. Create admin service layer
5. Add tests for admin APIs

### Phase 4: Public APIs (Week 4)
1. Implement notice endpoints
2. Implement requests-by-week endpoints
3. Implement user-action-verification endpoints
4. Implement consumer registration
5. Implement producer registration

### Phase 5: Instagram Features (Week 5)
1. Implement unfollow checker
2. Integrate helper account rotation
3. Implement session management
4. Add Instagram rate limiting
5. Test Instagram integrations

### Phase 6: Testing & Documentation (Week 6)
1. Write unit tests for all services
2. Write integration tests for all APIs
3. Create API documentation
4. Set up CI/CD pipeline
5. Performance testing and optimization

### Phase 7: Deployment (Week 7)
1. Configure production settings
2. Set up database migrations
3. Deploy to production environment
4. Monitor and fix issues
5. Create admin user accounts

---

## Pydantic Schemas Overview

### Common Schemas

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/schemas/common.py

from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    message: str = None
```

### Example Entity Schemas

```python
# /Users/iymaeng/Documents/private/autogram-latest/api/schemas/sns_raise_user.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class SnsRaiseUserBase(BaseModel):
    """Base schema for SNS Raise User"""
    username: str = Field(..., min_length=1, max_length=255, description="Instagram username")

class SnsRaiseUserCreate(SnsRaiseUserBase):
    """Schema for creating SNS Raise User"""
    pass

class SnsRaiseUserUpdate(BaseModel):
    """Schema for updating SNS Raise User"""
    username: Optional[str] = Field(None, min_length=1, max_length=255)

class SnsRaiseUserResponse(SnsRaiseUserBase):
    """Schema for SNS Raise User response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
```

---

## Technology Stack Summary

### Core Dependencies

```txt
# /Users/iymaeng/Documents/private/autogram-latest/requirements.txt

# FastAPI & Web
fastapi==0.115.0
uvicorn[standard]==0.31.0
python-multipart==0.0.12

# Database
sqlalchemy==2.0.35
asyncpg==0.29.0
alembic==1.13.3

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==43.0.1

# Instagram
instaloader==4.13
instagrapi==2.1.2

# Settings & Validation
pydantic==2.9.2
pydantic-settings==2.5.2

# Utilities
python-dotenv==1.0.1

# Testing
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

---

## Key Design Decisions

### 1. Async-First Architecture
- All database operations use SQLAlchemy async
- Instagram operations wrapped with `asyncio.to_thread` for non-blocking execution
- FastAPI async route handlers for better concurrency

### 2. Separation of Concerns
- **Models**: Database schema (SQLAlchemy)
- **Schemas**: API contracts (Pydantic)
- **Repositories**: Data access logic
- **Services**: Business logic
- **Routers**: HTTP endpoints

### 3. Security
- JWT tokens for admin authentication
- Password hashing with bcrypt (admin passwords)
- Symmetric encryption with Fernet (Instagram passwords)
- Session-based Instagram authentication

### 4. Instagram Integration
- Helper accounts for read operations (rotation strategy)
- Producer accounts for write operations
- Session persistence to avoid repeated logins
- Rate limiting and delays to avoid bans

### 5. Error Handling
- Custom exception classes
- Global exception handlers
- Consistent error response format
- Proper HTTP status codes

### 6. Testing Strategy
- Unit tests for services and repositories
- Integration tests for API endpoints
- Mock Instagram clients for testing
- Pytest fixtures for common test data

### 7. Scalability Considerations
- Database connection pooling
- Async operations for I/O-bound tasks
- Helper account rotation for load distribution
- Pagination for large datasets

---

## Next Steps for Implementation

1. **Review this architecture** with your team
2. **Create the directory structure** as outlined
3. **Set up the database** and create initial migration
4. **Implement core infrastructure** (config, database session, base models)
5. **Start with admin APIs** (authentication, SNS users, helpers)
6. **Implement public APIs** progressively
7. **Add Instagram integrations** with proper testing
8. **Write comprehensive tests**
9. **Deploy to production**

---

## Additional Resources

### File Locations Reference

All file paths are absolute paths from the project root:
- **Project Root**: `/Users/iymaeng/Documents/private/autogram-latest/`
- **API Directory**: `/Users/iymaeng/Documents/private/autogram-latest/api/`
- **Batch Directory**: `/Users/iymaeng/Documents/private/autogram-latest/batch/`
- **Core Directory**: `/Users/iymaeng/Documents/private/autogram-latest/core/`
- **Tests Directory**: `/Users/iymaeng/Documents/private/autogram-latest/tests/`

### Environment Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Run development server
uvicorn api.index:app --reload --port 8000
```

---

**End of Architecture Document**
