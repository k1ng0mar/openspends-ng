"""Analytics endpoints for dashboard charts and geographic data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db

router = APIRouter()


@router.get("/budget-spending-variance")
async def budget_spending_variance(
    mda_id: Optional[int] = None,
    year: Optional[int] = None,
    state_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """
    Returns budgeted vs actual spending data formatted for D3.js charts.
    Response: { data: [{ year, mda_id, mda_name, budgeted, spent, variance_pct }] }
    """
    return {"data": []}


@router.get("/geographic")
async def geographic_heatmap(
    year: Optional[int] = None,
    type: str = Query("spent", pattern="^(spent|budgeted|project_count)$"),
    level: str = Query("state", pattern="^(state|lga)$"),
    db: Session = Depends(get_db),
):
    """
    Returns GeoJSON FeatureCollection for Mapbox choropleth/heatmap layers.
    """
    return {
        "type": "FeatureCollection",
        "features": []
    }
