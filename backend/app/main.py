"""OpenSpends NG — FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Start the background scheduler
    try:
        from app.services.scheduler import start_scheduler
        start_scheduler()
    except Exception as e:
        # Don't crash the app if scheduler fails to start
        import logging
        logging.getLogger(__name__).warning(f"Scheduler failed to start: {e}")

    yield

    # Shutdown: stop the scheduler
    try:
        from app.services.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Track Nigerian government budget allocation & spending",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/debug/db")
async def debug_db():
    """Test database connection."""
    from app.core.database import engine
    from sqlalchemy import text
    from app.core.config import settings
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM projects"))
            count = result.scalar()
            return {
                "status": "connected",
                "project_count": count,
                "db_url_host": str(engine.url.host) if engine.url.host else "none",
                "settings_database_url": settings.DATABASE_URL[:50] + "..."
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:200],
            "settings_database_url": settings.DATABASE_URL[:50] + "..."
        }
