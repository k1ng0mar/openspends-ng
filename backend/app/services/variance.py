"""Spending Variance Analysis Engine.

Compares allocated (budget) vs spent amounts per MDA and flags:
  - OVER_UTILIZATION: spending > 110% of allocation
  - UNDER_UTILIZATION: spending < 20% of allocation
  - ON_TRACK: spending between 20% and 110% of allocation
"""

import io
import csv
import json
from datetime import date
from enum import Enum
from typing import Optional

from fastapi import Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models import Budget, Spending, MDA, State, FiscalYear, NCOA

# ── Column presence detection (model introspection) ────────────

_BUDGET_HAS_STATE = hasattr(Budget, "state_id")
_BUDGET_HAS_TYPE = hasattr(Budget, "budget_type")
_SPENDING_HAS_YEAR = hasattr(Spending, "year_id")
_SPENDING_HAS_STATE = hasattr(Spending, "state_id")


class VarianceFlag(str, Enum):
    OVER_UTILIZATION = "over_utilization"
    UNDER_UTILIZATION = "under_utilization"
    ON_TRACK = "on_track"


# Thresholds
OVER_THRESHOLD = 1.10   # >110% of allocation → over-utilization
UNDER_THRESHOLD = 0.20  # <20% of allocation → under-utilization


def compute_variance_flags(
    db: Session,
    year: Optional[int] = None,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    budget_type: Optional[str] = None,
    flag_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    """
    Compute per-MDA variance between allocated and spent amounts.

    Aggregates budgets by MDA, sums actual spending, and returns
    utilization flags for each MDA.

    Args:
        db: Database session.
        year: Fiscal year filter (optional).
        mda_id: Single MDA filter (optional).
        state_id: State filter (optional).
        budget_type: 'national' or 'state' (optional).
        flag_filter: Filter by variance flag ('over_utilization', 'under_utilization', 'on_track').
        page: Page number (1-indexed).
        page_size: Results per page.

    Returns:
        {
            "data": [VarianceFlagItem, ...],
            "total": int,
            "page": int,
            "page_size": int,
            "pages": int,
            "summary": {
                "total_mdas": int,
                "over_utilized": int,
                "under_utilized": int,
                "on_track": int
            }
        }
    """
    # ── Aggregate budgets per MDA ──────────────────────────────────
    budget_q = (
        db.query(
            Budget.mda_id,
            func.sum(Budget.approved).label("total_approved"),
            func.sum(Budget.revised).label("total_revised"),
            func.sum(Budget.estimated).label("total_estimated"),
            func.sum(Budget.spent).label("total_spent_from_budget"),
            func.count(Budget.id).label("budget_line_count"),
        )
    )

    if year is not None:
        budget_q = budget_q.join(FiscalYear, Budget.year_id == FiscalYear.id)
        budget_q = budget_q.filter(FiscalYear.year == year)
    if state_id is not None and _BUDGET_HAS_STATE:
        budget_q = budget_q.filter(Budget.state_id == state_id)
    if budget_type is not None and _BUDGET_HAS_TYPE:
        budget_q = budget_q.filter(Budget.budget_type == budget_type)

    budget_q = budget_q.group_by(Budget.mda_id)
    budget_rows = budget_q.all()

    # ── Aggregate actual spending per MDA ──────────────────────────
    spending_q = (
        db.query(
            Spending.mda_id,
            func.sum(Spending.amount).label("total_spent_actual"),
            func.count(Spending.id).label("spending_tx_count"),
        )
    )
    if year is not None and _SPENDING_HAS_YEAR:
        spending_q = spending_q.join(FiscalYear, Spending.year_id == FiscalYear.id)
        spending_q = spending_q.filter(FiscalYear.year == year)
    if state_id is not None and _SPENDING_HAS_STATE:
        spending_q = spending_q.filter(Spending.state_id == state_id)
    if mda_id is not None:
        spending_q = spending_q.filter(Spending.mda_id == mda_id)

    spending_q = spending_q.group_by(Spending.mda_id)
    spending_map = {row.mda_id: row for row in spending_q.all()}

    # ── Build variance results ─────────────────────────────────────
    results = []
    for b_row in budget_rows:
        mda_id_val = b_row.mda_id
        allocated = float(b_row.total_approved or 0)

        # Prefer actual spending from Spending table; fall back to budget.spent column
        spent_actual = 0.0
        s_row = spending_map.get(mda_id_val)
        if s_row and s_row.total_spent_actual:
            spent_actual = float(s_row.total_spent_actual)
        elif b_row.total_spent_from_budget:
            spent_actual = float(b_row.total_spent_from_budget)

        # Variance calculation
        if allocated > 0:
            utilization_pct = round((spent_actual / allocated) * 100, 2)
            variance_amount = round(spent_actual - allocated, 2)
            variance_pct = round(((spent_actual - allocated) / allocated) * 100, 2)
        else:
            utilization_pct = 0.0
            variance_amount = spent_actual
            variance_pct = 0.0

        # Flag assignment
        if utilization_pct > 110:
            flag = VarianceFlag.OVER_UTILIZATION
        elif utilization_pct < 20:
            flag = VarianceFlag.UNDER_UTILIZATION
        else:
            flag = VarianceFlag.ON_TRACK

        # MDA info
        mda = db.query(MDA).filter(MDA.id == mda_id_val).first()
        mda_name = mda.name if mda else f"MDA #{mda_id_val}"
        mda_code = mda.code if mda else None

        item = {
            "mda_id": mda_id_val,
            "mda_name": mda_name,
            "mda_code": mda_code,
            "year": year,
            "allocated": allocated,
            "spent": spent_actual,
            "variance_amount": variance_amount,
            "variance_pct": variance_pct,
            "utilization_pct": utilization_pct,
            "flag": flag.value,
            "budget_lines": b_row.budget_line_count,
            "spending_transactions": s_row.spending_tx_count if s_row else 0,
        }
        results.append(item)

    # Filter by MDA if specified (when no budget row matched, check spending-only MDAs)
    if mda_id is not None:
        results = [r for r in results if r["mda_id"] == mda_id]

    # Apply flag filter
    summary = {
        "total_mdas": len(results),
        "over_utilized": sum(1 for r in results if r["flag"] == VarianceFlag.OVER_UTILIZATION),
        "under_utilized": sum(1 for r in results if r["flag"] == VarianceFlag.UNDER_UTILIZATION),
        "on_track": sum(1 for r in results if r["flag"] == VarianceFlag.ON_TRACK),
    }

    if flag_filter:
        results = [r for r in results if r["flag"] == flag_filter]

    # Sort: over-utilized first, then under-utilized, then on-track
    flag_order = {
        VarianceFlag.OVER_UTILIZATION.value: 0,
        VarianceFlag.UNDER_UTILIZATION.value: 1,
        VarianceFlag.ON_TRACK.value: 2,
    }
    results.sort(key=lambda r: (flag_order.get(r["flag"], 3), -abs(r["variance_pct"])))

    # Pagination
    total = len(results)
    pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = results[start:end]

    return {
        "data": paginated,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "summary": summary,
    }


def export_variance_csv(variance_result: dict) -> StreamingResponse:
    """Export variance analysis results as CSV download."""
    FIELDNAMES = [
        "mda_id", "mda_name", "mda_code", "year",
        "allocated", "spent", "variance_amount", "variance_pct",
        "utilization_pct", "flag", "budget_lines", "spending_transactions",
    ]
    rows = variance_result.get("data", [])
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    csv_text = buf.getvalue()

    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=openspends_variance_analysis.csv"},
    )


def export_variance_json(variance_result: dict) -> StreamingResponse:
    """Export variance analysis results as JSON download."""
    json_bytes = json.dumps(variance_result, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_bytes.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=openspends_variance_analysis.json"},
    )
