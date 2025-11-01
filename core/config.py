"""
Configuration module for Autogram project.
Loads environment variables and provides application settings.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/autogram"

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Encryption key for passwords (Fernet key - must be 32 url-safe base64-encoded bytes)
    ENCRYPTION_KEY: str = "your-encryption-key-here-change-in-production"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://autogram.example.com"
    ]

    # Instagram
    INSTAGRAM_SESSION_DIR: str = "/tmp/instagram_sessions"

    # API
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Autogram API"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",  # Look in root directory
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
