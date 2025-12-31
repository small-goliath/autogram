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

    pending = "pending"
    active = "active"
    inactive = "inactive"


class Admin(Base):
    """Admin account model."""

    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
    )


class SnsRaiseUser(Base):
    """SNS 품앗이 사용자 model."""

    __tablename__ = "sns_raise_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
    )

    # Relationships
    requests: Mapped[list["RequestByWeek"]] = relationship(
        "RequestByWeek",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="RequestByWeek.username",
    )
    verifications: Mapped[list["UserActionVerification"]] = relationship(
        "UserActionVerification",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="UserActionVerification.username",
    )
    link_owner_verifications: Mapped[list["UserActionVerification"]] = relationship(
        "UserActionVerification",
        back_populates="link_owner",
        cascade="all, delete-orphan",
        foreign_keys="UserActionVerification.link_owner_username",
    )


class RequestByWeek(Base):
    """주간 링크 요청 기록."""

    __tablename__ = "request_by_week"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        nullable=False,
    )
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    week_start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser", back_populates="requests", foreign_keys=[username]
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
        nullable=False,
    )
    instagram_link: Mapped[str] = mapped_column(String(500), nullable=False)
    link_owner_username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )

    # Relationships
    user: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser", back_populates="verifications", foreign_keys=[username]
    )
    link_owner: Mapped["SnsRaiseUser"] = relationship(
        "SnsRaiseUser",
        back_populates="link_owner_verifications",
        foreign_keys=[link_owner_username],
    )

    __table_args__ = (
        Index("idx_username", "username"),
        Index("idx_link", "instagram_link"),
    )


class Consumer(Base):
    """AI 자동 댓글 받기 신청자."""

    __tablename__ = "consumer"

    instagram_username: Mapped[str] = mapped_column(
        String(100), primary_key=True, nullable=False
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.pending, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
    )


class Producer(Base):
    """AI 자동 댓글 달기 신청자 (instagrapi용)."""

    __tablename__ = "producer"

    instagram_username: Mapped[str] = mapped_column(
        String(100), primary_key=True, nullable=False
    )
    instagram_password: Mapped[str] = mapped_column(String(255), nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.pending, nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
    )


class UnfollowerServiceUser(Base):
    """언팔로워 검색 서비스 사용자."""

    __tablename__ = "unfollower_service_user"

    username: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(String(150), nullable=False)
    totp_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship
    sns_raise_user: Mapped["SnsRaiseUser"] = relationship("SnsRaiseUser")


class Unfollower(Base):
    """언팔로워 목록."""

    __tablename__ = "unfollowers"

    owner: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("sns_raise_user.username", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    unfollower_username: Mapped[str] = mapped_column(
        String(50), primary_key=True, nullable=False
    )
    unfollower_fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    unfollower_profile_url: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, nullable=False
    )

    # Relationship
    owner_user: Mapped["SnsRaiseUser"] = relationship("SnsRaiseUser")
