"""Budget endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas import BudgetOut

router = APIRouter()


@router.get("/mda/{mda_id}", response_model=list[BudgetOut])
async def get_mda_budgets(
    mda_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get budget allocations for an MDA, optionally filtered by year."""
    return []


@router.get("/state/{state_id}", response_model=list[BudgetOut])
async def get_state_budgets(
    state_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get aggregated budget for a state."""
    return []
