"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "OpenSpends NG"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/openspends"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Mapbox
    MAPBOX_TOKEN: str = ""

    # GitHub (for issue creation)
    GITHUB_TOKEN: str = ""

    # Rate Limiting
    RATE_LIMIT_PUBLIC: int = 100
    RATE_LIMIT_AUTH: int = 1000

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
