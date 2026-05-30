"""Capital project endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Any

from app.core.database import get_db
from app.models.project import Project
from app.models.mda import MDA
from app.models.state import State
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
    """List capital projects with filters. Supports GeoJSON output for map rendering."""
    query = db.query(Project)

    if state_id:
        query = query.filter(Project.state_id == state_id)
    if lga_id:
        query = query.filter(Project.lga_id == lga_id)
    if status:
        query = query.filter(Project.status == status)
    if mda_id:
        query = query.filter(Project.mda_id == mda_id)
    if year:
        query = query.filter(func.extract('year', Project.start_date) == year)

    # Pagination
    offset = (page - 1) * page_size
    projects = query.offset(offset).limit(page_size).all()

    # Convert to output schema with lat/lng extraction
    result = []
    for p in projects:
        lat, lng = None, None
        if p.geolocation:
            # Extract lat/lng from PostGIS geometry
            geom = db.execute(func.ST_AsText(p.geolocation)).scalar()
            if geom and geom.startswith('POINT('):
                # Parse POINT(lng lat)
                coords = geom[6:-1].split()
                lng, lat = float(coords[0]), float(coords[1])

        result.append(ProjectOut(
            id=p.id,
            title=p.title,
            mda_id=p.mda_id,
            state_id=p.state_id,
            lga_id=p.lga_id,
            contractor=p.contractor,
            start_date=p.start_date,
            end_date=p.end_date,
            status=p.status,
            budget_allocated=p.budget_allocated,
            spent=p.spent,
            latitude=lat,
            longitude=lng,
            source=p.source,
        ))

    return result


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get full project detail including timeline and linked documents."""
    p = db.query(Project).filter(Project.id == project_id).first()
    if not p:
        return None

    lat, lng = None, None
    if p.geolocation:
        geom = db.execute(func.ST_AsText(p.geolocation)).scalar()
        if geom and geom.startswith('POINT('):
            coords = geom[6:-1].split()
            lng, lat = float(coords[0]), float(coords[1])

    return ProjectOut(
        id=p.id,
        title=p.title,
        mda_id=p.mda_id,
        state_id=p.state_id,
        lga_id=p.lga_id,
        contractor=p.contractor,
        start_date=p.start_date,
        end_date=p.end_date,
        status=p.status,
        budget_allocated=p.budget_allocated,
        spent=p.spent,
        latitude=lat,
        longitude=lng,
        source=p.source,
    )
