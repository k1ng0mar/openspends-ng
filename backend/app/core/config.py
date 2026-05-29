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

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    @property
    def database_url(self) -> str:
        """Return Supabase connection string or local DATABASE_URL."""
        if self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY:
            return (
                f"postgresql+psycopg://postgres:{self.SUPABASE_SERVICE_KEY}"
                f"@aws-0-eu-west-1.pooler.supabase.com:6543/postgres"
                f"?sslmode=require"
            )
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
