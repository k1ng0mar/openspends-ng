"""Capital project endpoints using Supabase REST API."""

from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from app.core.config import settings
from app.core.supabase_client import SupabaseClient
from app.schemas import ProjectOut

router = APIRouter()


def get_supabase() -> SupabaseClient:
    return SupabaseClient(
        url=settings.SUPABASE_URL,
        anon_key=settings.SUPABASE_KEY,
        service_key=settings.SUPABASE_SERVICE_KEY
    )


@router.get("/", response_model=List[ProjectOut])
async def list_projects(
    state_id: Optional[int] = None,
    lga_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(not_started|in_progress|completed|abandoned)$"),
    mda_id: Optional[int] = None,
    year: Optional[int] = None,
    format: str = Query("json", pattern="^(json|geojson)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    supabase: SupabaseClient = Depends(get_supabase),
):
    """List capital projects with filters."""
    offset = (page - 1) * page_size
    
    projects_data = await supabase.get_projects(
        state_id=state_id,
        status=status,
        mda_id=mda_id,
        limit=page_size,
        offset=offset
    )
    
    projects = []
    for p in projects_data:
        projects.append(ProjectOut(
            id=p["id"],
            title=p["title"],
            mda_id=p.get("mda_id"),
            state_id=p["state_id"],
            lga_id=p.get("lga_id"),
            contractor=p.get("contractor"),
            start_date=p.get("start_date"),
            end_date=p.get("end_date"),
            status=p["status"],
            budget_allocated=float(p["budget_allocated"]) if p.get("budget_allocated") else None,
            spent=float(p["spent"]) if p.get("spent") else None,
            latitude=p.get("latitude"),
            longitude=p.get("longitude"),
            source=p.get("source"),
        ))
    
    return projects


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: int,
    supabase: SupabaseClient = Depends(get_supabase)
):
    """Get full project detail."""
    p = await supabase.get_project(project_id)
    
    if not p:
        return None
    
    return ProjectOut(
        id=p["id"],
        title=p["title"],
        mda_id=p.get("mda_id"),
        state_id=p["state_id"],
        lga_id=p.get("lga_id"),
        contractor=p.get("contractor"),
        start_date=p.get("start_date"),
        end_date=p.get("end_date"),
        status=p["status"],
        budget_allocated=float(p["budget_allocated"]) if p.get("budget_allocated") else None,
        spent=float(p["spent"]) if p.get("spent") else None,
        latitude=p.get("latitude"),
        longitude=p.get("longitude"),
        source=p.get("source"),
    )
