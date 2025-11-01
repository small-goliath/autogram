"""
SQLAlchemy ORM models for all database tables.
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base
from .utils import get_kst_now


class StatusEnum(str, PyEnum):
    """Status enum for consumer and producer tables."""
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class Admin(Base):
    """Admin account model."""
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )


class SnsRaiseUser(Base):
    """SNS 품앗이 사용자 model."""
    __tablename__ = "sns_raise_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )

    # Relationships
    requests: Mapped[list["RequestByWeek"]] = relationship(
        "RequestByWeek",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="RequestByWeek.username"
    )
    verifications: Mapped[list["UserActionVerification"]] = relationship(
        "UserActionVerification",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserActionVerification.username"
    )
    link_owner_verifications: Mapped[list["UserActionVerification"]] = relationship(
        "UserActionVerification",
        back_populates="link_owner",
        cascade="all, delete-orphan",
        foreign_keys="UserActionVerification.link_owner_username"
    )


class Helper(Base):
    """Instagram helper account (instaloader용, 단순 조회)."""
    __tablename__ = "helper"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    instagram_password: Mapped[str] = mapped_column(String(255), nullable=False)
    session_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )


class RequestByWeek(Base):
    """주간 링크 요청 기록."""
    __tablename__ = "request_by_week"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        nullable=False
    )
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    week_start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser",
        back_populates="requests",
        foreign_keys=[username]
    )

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_week_start_date", "week_start_date"),
    )


class UserActionVerification(Base):
    """댓글 작성 검증 (미작성자 추적)."""
    __tablename__ = "user_action_verification"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        nullable=False
    )
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    link_owner_username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser",
        back_populates="verifications",
        foreign_keys=[username]
    )
    link_owner: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser",
        back_populates="link_owner_verifications",
        foreign_keys=[link_owner_username]
    )

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_link", "instagram_link"),
    )


class VerificationRetryQueue(Base):
    """검증 실패 재시도 큐 (Rate Limit 등으로 실패한 포스트 조회 재시도)."""
    __tablename__ = "verification_retry_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    shortcode: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    batch_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="verify 또는 cleanup"
    )
    link_owner_username: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="verify 배치의 경우 링크 소유자"
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True,
        comment="pending, processing, completed, failed"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )

    __table_args__ = (
        Index("idx_status_batch", "status", "batch_type"),
        Index("idx_shortcode", "shortcode"),
        # Partial unique index (created in migration):
        # CREATE UNIQUE INDEX idx_unique_pending_shortcode_batch
        # ON verification_retry_queue (shortcode, batch_type)
        # WHERE status IN ('pending', 'processing')
    )


class Consumer(Base):
    """AI 자동 댓글 받기 신청자."""
    __tablename__ = "consumer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        default=StatusEnum.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )


class Producer(Base):
    """AI 자동 댓글 달기 신청자 (instagrapi용)."""
    __tablename__ = "producer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    instagram_username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    instagram_password: Mapped[str] = mapped_column(String(255), nullable=False)
    verification_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    session_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum),
        default=StatusEnum.PENDING,
        nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )


class Announcement(Base):
    """공지사항."""
    __tablename__ = "announcement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    kakao_openchat_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    kakao_qr_code_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_kst_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_kst_now,
        onupdate=get_kst_now,
        nullable=False
    )
