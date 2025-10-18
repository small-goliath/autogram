"""Database models shared between API and Batch."""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from core.database import Base


class SnsRaiseUser(Base):
    """Users participating in the SNS exchange service."""
    __tablename__ = "sns_raise_user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    instagram_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    requests: Mapped[list["RequestByWeek"]] = relationship("RequestByWeek", back_populates="user", cascade="all, delete-orphan")
    actions: Mapped[list["UserActionVerification"]] = relationship("UserActionVerification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<SnsRaiseUser(id={self.id}, username='{self.username}')>"


class RequestByWeek(Base):
    """Weekly Instagram link submissions from users."""
    __tablename__ = "request_by_week"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sns_raise_user.id", ondelete="CASCADE"), nullable=False)
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    request_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    week_start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    week_end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, completed, failed
    comment_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship("SnsRaiseUser", back_populates="requests")

    # Indexes
    __table_args__ = (
        Index('idx_user_week', 'user_id', 'week_start_date'),
    )

    def __repr__(self) -> str:
        return f"<RequestByWeek(id={self.id}, user_id={self.user_id}, link='{self.instagram_link[:30]}...')>"


class UserActionVerification(Base):
    """Tracks which users haven't commented on which links."""
    __tablename__ = "user_action_verification"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sns_raise_user.id", ondelete="CASCADE"), nullable=False)
    request_id: Mapped[int] = mapped_column(ForeignKey("request_by_week.id", ondelete="CASCADE"), nullable=False)
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    link_owner_username: Mapped[str] = mapped_column(String(100), nullable=False)
    is_commented: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship("SnsRaiseUser", back_populates="actions")

    # Indexes
    __table_args__ = (
        Index('idx_user_request', 'user_id', 'request_id'),
        Index('idx_is_commented', 'is_commented'),
    )

    def __repr__(self) -> str:
        return f"<UserActionVerification(id={self.id}, user_id={self.user_id}, is_commented={self.is_commented})>"


class Helper(Base):
    """Helper Instagram accounts for read-only operations."""
    __tablename__ = "helper"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    instagram_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    instagram_password_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    session_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Pickled session
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    login_attempts: Mapped[int] = mapped_column(default=0, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Helper(id={self.id}, instagram_id='{self.instagram_id}', is_active={self.is_active})>"


class Consumer(Base):
    """Users who want to receive AI auto-comments on their posts."""
    __tablename__ = "consumer"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    instagram_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    comment_tone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # friendly, professional, casual, enthusiastic
    special_requests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Consumer(id={self.id}, instagram_id='{self.instagram_id}')>"


class Producer(Base):
    """Users who provide their accounts for AI commenting."""
    __tablename__ = "producer"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    instagram_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    instagram_password_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    session_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verification_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Producer(id={self.id}, instagram_id='{self.instagram_id}')>"


class Admin(Base):
    """Admin users who can access admin panel."""
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, username='{self.username}')>"


class Notice(Base):
    """Announcements and notices for users."""
    __tablename__ = "notice"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = mapped_column(default=0, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("admin.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<Notice(id={self.id}, title='{self.title}')>"
