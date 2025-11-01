"""
Database connection and session management.
Provides async SQLAlchemy engine and session maker.
"""
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase
from .config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Global engine and session maker
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create async SQLAlchemy engine.

    Returns:
        AsyncEngine instance
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        # Use DATABASE_URL as-is (should be postgresql+asyncpg:// format)
        # Pool size optimized for free tier (Session Mode limits)
        _engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=5,       # 무료 플랜: API + 배치 동시 실행 가능하도록 작게 설정
            max_overflow=0,    # Session Mode에서는 추가 연결 생성 불가
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get or create async session maker.

    Returns:
        Async session maker
    """
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Use with FastAPI Depends().

    Yields:
        AsyncSession instance
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database engine and connections.
    Should be called on application shutdown.
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
