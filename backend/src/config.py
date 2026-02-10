"""Application configuration."""

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database (asyncpg for local PostgreSQL)
    database_url: str = (
        "postgresql+asyncpg://studyhelper:studyhelper@127.0.0.1:5432/studyhelper"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"

    # Application
    debug: bool = True
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Schedule parser
    schedule_url: str = "https://eservice.omsu.ru/schedule/#/schedule/group/5028"
    schedule_update_interval_hours: int = 6
    schedule_sync_enabled: bool = True
    schedule_sync_lock_ttl_seconds: int = 600

    # File uploads
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 5
    allowed_image_types: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # Study file uploads
    max_file_size_mb: int = 50
    allowed_file_extensions: list[str] = [
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
    ]
    allowed_file_mime_types: list[str] = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    ]

    # Timezone
    timezone: str = "Asia/Omsk"

    @model_validator(mode="after")
    def validate_secret_key(self) -> "Settings":
        """Ensure secret_key is changed in production."""
        if not self.debug and self.secret_key == "change-me-in-production":
            raise ValueError(
                "secret_key must be changed from default in production (debug=False)"
            )
        return self


settings = Settings()
