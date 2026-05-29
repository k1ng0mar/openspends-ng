"""Capital project endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas import ProjectOut

router = APIRouter()


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    state_id: Optional[int] = None,
    lga_id: Optional[int] = None,
    status: Optional[str] = Query(None, regex="^(not_started|in_progress|completed|abandoned)$"),
    mda_id: Optional[int] = None,
    year: Optional[int] = None,
    format: str = Query("json", regex="^(json|geojson)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List capital projects with filters. Supports GeoJSON output for map rendering."""
    return []


@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get full project detail including timeline and linked documents."""
    return {}
