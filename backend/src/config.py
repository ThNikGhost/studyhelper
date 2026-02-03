"""Application configuration."""

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


settings = Settings()
