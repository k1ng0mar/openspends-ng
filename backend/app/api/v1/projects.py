"""Capital project endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from app.core.database import get_db
from app.schemas import ProjectOut

router = APIRouter()


@router.get("/", response_model=list[ProjectOut])
async def list_projects(
    state_id: Optional[int] = None,
    lga_id: Optional[int] = None,
    status: Optional[str] = Query(None, pattern="^(not_started|in_progress|completed|abandoned)$"),
    mda_id: Optional[int] = None,
    year: Optional[int] = None,
    format: str = Query("json", pattern="^(json|geojson)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List capital projects with filters."""
    # Simple query without PostGIS for now
    query_str = """
        SELECT 
            id, title, mda_id, state_id, lga_id, contractor,
            start_date, end_date, status, budget_allocated, spent, source
        FROM projects
        WHERE 1=1
    """
    
    params = {}
    if state_id:
        query_str += " AND state_id = :state_id"
        params["state_id"] = state_id
    if status:
        query_str += " AND status = :status"
        params["status"] = status
    if mda_id:
        query_str += " AND mda_id = :mda_id"
        params["mda_id"] = mda_id

    offset = (page - 1) * page_size
    query_str += f" LIMIT {page_size} OFFSET {offset}"

    try:
        result = db.execute(text(query_str), params)
        rows = result.fetchall()
    except Exception as e:
        print(f"DB Error: {e}")
        return []

    projects = []
    for row in rows:
        projects.append(ProjectOut(
            id=row.id,
            title=row.title,
            mda_id=row.mda_id,
            state_id=row.state_id,
            lga_id=row.lga_id,
            contractor=row.contractor,
            start_date=row.start_date,
            end_date=row.end_date,
            status=row.status,
            budget_allocated=float(row.budget_allocated) if row.budget_allocated else None,
            spent=float(row.spent) if row.spent else None,
            latitude=None,
            longitude=None,
            source=row.source,
        ))

    return projects


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get full project detail."""
    query_str = """
        SELECT 
            id, title, mda_id, state_id, lga_id, contractor,
            start_date, end_date, status, budget_allocated, spent, source
        FROM projects
        WHERE id = :project_id
    """
    
    try:
        result = db.execute(text(query_str), {"project_id": project_id})
        row = result.fetchone()
    except Exception as e:
        print(f"DB Error: {e}")
        return None

    if not row:
        return None

    return ProjectOut(
        id=row.id,
        title=row.title,
        mda_id=row.mda_id,
        state_id=row.state_id,
        lga_id=row.lga_id,
        contractor=row.contractor,
        start_date=row.start_date,
        end_date=row.end_date,
        status=row.status,
        budget_allocated=float(row.budget_allocated) if row.budget_allocated else None,
        spent=float(row.spent) if row.spent else None,
        latitude=None,
        longitude=None,
        source=row.source,
    )
