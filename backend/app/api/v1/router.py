"""API v1 route aggregator."""

from fastapi import APIRouter

from app.api.v1 import mdas, budgets, spending, projects, analytics, geocode, pipeline

api_router = APIRouter()

api_router.include_router(mdas.router, prefix="/mdas", tags=["MDAs"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(spending.router, prefix="/spending", tags=["Spending"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(geocode.router, prefix="/geocode", tags=["Geocoding"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Pipeline"])
