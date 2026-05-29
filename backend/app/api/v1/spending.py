"""Spending (actual payments) endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.schemas import SpendingOut

router = APIRouter()


@router.get("/", response_model=list[SpendingOut])
async def list_spending(
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    amount_min: Optional[float] = Query(None, description="Minimum amount (NGN)"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List actual government payments with filters."""
    return []
