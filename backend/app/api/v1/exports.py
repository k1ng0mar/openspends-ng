"""Data export endpoints — generate CSV and JSON downloads for filtered budget & spending data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.schemas import ExportFormatResponse
from app.services.export import (
    export_budget_csv,
    export_budget_json,
    export_spending_csv,
    export_spending_json,
)
from app.services.variance import compute_variance_flags, export_variance_csv, export_variance_json

router = APIRouter()


@router.get("/formats")
async def export_formats():
    """List available export formats and filters."""
    return ExportFormatResponse()


# ── Budget Exports ────────────────────────────────────────────────

@router.get("/budgets.csv")
async def export_budgets_csv(
    mda_id: Optional[int] = Query(None, description="Filter by MDA ID"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    year: Optional[int] = Query(None, description="Fiscal year"),
    ncoa_code: Optional[str] = Query(None, description="NCOA code prefix"),
    budget_type: Optional[str] = Query(None, description="Budget type: national or state"),
    db: Session = Depends(get_db),
):
    """Download filtered budget data as CSV."""
    return export_budget_csv(
        db, mda_id=mda_id, state_id=state_id, year=year,
        ncoa_code=ncoa_code, budget_type=budget_type,
    )


@router.get("/budgets.json")
async def export_budgets_json(
    mda_id: Optional[int] = Query(None, description="Filter by MDA ID"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    year: Optional[int] = Query(None, description="Fiscal year"),
    ncoa_code: Optional[str] = Query(None, description="NCOA code prefix"),
    budget_type: Optional[str] = Query(None, description="Budget type: national or state"),
    db: Session = Depends(get_db),
):
    """Download filtered budget data as JSON."""
    return export_budget_json(
        db, mda_id=mda_id, state_id=state_id, year=year,
        ncoa_code=ncoa_code, budget_type=budget_type,
    )


# ── Spending Exports ──────────────────────────────────────────────

@router.get("/spending.csv")
async def export_spending_csv(
    mda_id: Optional[int] = Query(None, description="Filter by MDA ID"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    year: Optional[int] = Query(None, description="Fiscal year"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    amount_min: Optional[float] = Query(None, description="Minimum amount (NGN)"),
    amount_max: Optional[float] = Query(None, description="Maximum amount (NGN)"),
    db: Session = Depends(get_db),
):
    """Download filtered spending data as CSV."""
    return export_spending_csv(
        db, mda_id=mda_id, state_id=state_id, year=year,
        date_from=date_from, date_to=date_to,
        amount_min=amount_min, amount_max=amount_max,
    )


@router.get("/spending.json")
async def export_spending_json(
    mda_id: Optional[int] = Query(None, description="Filter by MDA ID"),
    state_id: Optional[int] = Query(None, description="Filter by state ID"),
    year: Optional[int] = Query(None, description="Fiscal year"),
    date_from: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    amount_min: Optional[float] = Query(None, description="Minimum amount (NGN)"),
    amount_max: Optional[float] = Query(None, description="Maximum amount (NGN)"),
    db: Session = Depends(get_db),
):
    """Download filtered spending data as JSON."""
    return export_spending_json(
        db, mda_id=mda_id, state_id=state_id, year=year,
        date_from=date_from, date_to=date_to,
        amount_min=amount_min, amount_max=amount_max,
    )


# ── Variance Analysis Exports ─────────────────────────────────────

@router.get("/variance.csv")
async def export_variance_csv_endpoint(
    year: Optional[int] = Query(None, description="Fiscal year"),
    mda_id: Optional[int] = Query(None, description="Single MDA filter"),
    state_id: Optional[int] = Query(None, description="State filter"),
    budget_type: Optional[str] = Query(None, description="Budget type"),
    flag: Optional[str] = Query(None, pattern="^(over_utilization|under_utilization|on_track)$"),
    db: Session = Depends(get_db),
):
    """Download full variance analysis as CSV."""
    result = compute_variance_flags(
        db=db, year=year, mda_id=mda_id, state_id=state_id,
        budget_type=budget_type, flag_filter=flag,
        page=1, page_size=10000,
    )
    return export_variance_csv(result)


@router.get("/variance.json")
async def export_variance_json_endpoint(
    year: Optional[int] = Query(None, description="Fiscal year"),
    mda_id: Optional[int] = Query(None, description="Single MDA filter"),
    state_id: Optional[int] = Query(None, description="State filter"),
    budget_type: Optional[str] = Query(None, description="Budget type"),
    flag: Optional[str] = Query(None, pattern="^(over_utilization|under_utilization|on_track)$"),
    db: Session = Depends(get_db),
):
    """Download full variance analysis as JSON."""
    result = compute_variance_flags(
        db=db, year=year, mda_id=mda_id, state_id=state_id,
        budget_type=budget_type, flag_filter=flag,
        page=1, page_size=10000,
    )
    return export_variance_json(result)
