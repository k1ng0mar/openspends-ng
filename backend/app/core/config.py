"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "OpenSpends NG"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"

    # Database — set DATABASE_URL or SUPABASE_URL (auto-converts)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/openspends"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Mapbox
    MAPBOX_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def database_url(self) -> str:
        """Return Supabase connection string or local DATABASE_URL."""
        if self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY:
            # Supabase Postgres format: postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
            project_ref = self.SUPABASE_URL.split("//")[1].split(".")[0]
            return f"postgresql+psycopg://postgres:{self.SUPABASE_SERVICE_KEY}@db.{project_ref}.supabase.co:5432/postgres?sslmode=require"
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
