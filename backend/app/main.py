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
    """Test Supabase REST API connection."""
    from app.core.supabase_client import SupabaseClient
    from app.core.config import settings
    
    try:
        client = SupabaseClient(
            url=settings.SUPABASE_URL,
            anon_key=settings.SUPABASE_KEY,
            service_key=settings.SUPABASE_SERVICE_KEY
        )
        count = await client.count_projects()
        return {
            "status": "connected",
            "project_count": count,
            "supabase_url": settings.SUPABASE_URL
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)[:200],
            "supabase_url": settings.SUPABASE_URL
        }
