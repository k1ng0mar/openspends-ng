"""Analysis endpoints — variance flags, researcher tools, and spending analytics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas import (
    VarianceAnalysisResponse,
    VarianceFlagItem,
    VarianceSummary,
)
from app.services.variance import compute_variance_flags

router = APIRouter()


@router.get("/variance", response_model=VarianceAnalysisResponse)
async def spending_variance_analysis(
    year: Optional[int] = Query(None, description="Fiscal year filter"),
    mda_id: Optional[int] = Query(None, description="Single MDA filter"),
    state_id: Optional[int] = Query(None, description="State filter"),
    budget_type: Optional[str] = Query(None, description="Budget type: national or state"),
    flag: Optional[str] = Query(
        None,
        description="Filter by variance flag",
        pattern="^(over_utilization|under_utilization|on_track)$",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    **Spending Variance Analysis**

    Compare allocated vs spent amounts per MDA and flag anomalies:
    - `over_utilization`: spending > 110% of allocation
    - `under_utilization`: spending < 20% of allocation
    - `on_track`: spending between 20% and 110%

    Results are sorted by severity (most over-budget first).
    Supports pagination and flag-based filtering.
    """
    result = compute_variance_flags(
        db=db,
        year=year,
        mda_id=mda_id,
        state_id=state_id,
        budget_type=budget_type,
        flag_filter=flag,
        page=page,
        page_size=page_size,
    )

    return VarianceAnalysisResponse(
        data=[VarianceFlagItem(**item) for item in result["data"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        pages=result["pages"],
        summary=VarianceSummary(**result["summary"]),
    )


@router.get("/variance/summary")
async def variance_summary(
    year: Optional[int] = Query(None, description="Fiscal year filter"),
    state_id: Optional[int] = Query(None, description="State filter"),
    budget_type: Optional[str] = Query(None, description="Budget type: national or state"),
    db: Session = Depends(get_db),
):
    """
    Quick summary counts for dashboard badges/widgets.
    Returns counts of MDAs by variance category.
    """
    result = compute_variance_flags(
        db=db,
        year=year,
        state_id=state_id,
        budget_type=budget_type,
        page=1,
        page_size=1,  # We only need the summary
    )
    return {
        "year": year,
        "state_id": state_id,
        "summary": result["summary"],
    }
