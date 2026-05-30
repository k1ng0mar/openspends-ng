"""MDA (Ministry/Department/Agency) endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas import MDAOut

router = APIRouter()


@router.get("/", response_model=list[MDAOut])
async def list_mdas(
    level: Optional[str] = Query(None, pattern="^(fed|state|lga)$"),
    state_id: Optional[int] = None,
    ncoa_sector: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List MDAs with optional filters."""
    # TODO: implement query with filters
    return []


@router.get("/{mda_id}", response_model=MDAOut)
async def get_mda(mda_id: int, db: Session = Depends(get_db)):
    """Get single MDA details."""
    # TODO: implement
    return {}
