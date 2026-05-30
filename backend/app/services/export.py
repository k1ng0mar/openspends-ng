"""Data export engine — generates CSV and JSON downloads for filtered spending/budget data."""

import csv
import io
import json
from datetime import date
from typing import Optional

from fastapi import Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select, and_, literal
from sqlalchemy.orm import Session

from app.models import Budget, Spending, MDA, State, FiscalYear, NCOA


# ── Column presence detection (model introspection) ────────────

_BUDGET_HAS_NCOA = hasattr(Budget, "ncoa_id")
_BUDGET_HAS_STATE = hasattr(Budget, "state_id")
_BUDGET_HAS_TYPE = hasattr(Budget, "budget_type")
_SPENDING_HAS_YEAR = hasattr(Spending, "year_id")
_SPENDING_HAS_STATE = hasattr(Spending, "state_id")


def _build_budget_query(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    budget_type: Optional[str] = None,
):
    """Build a filtered query joining Budget -> MDA -> FiscalYear.

    Optionally includes NCOA and State when those columns exist on the Budget model.
    """
    # Build select columns dynamically
    select_cols = [
        Budget.id.label("budget_id"),
        MDA.name.label("mda_name"),
        MDA.code.label("mda_code"),
        FiscalYear.year.label("fiscal_year"),
        Budget.season,
        Budget.approved,
        Budget.revised,
        Budget.estimated,
        Budget.spent,
        Budget.variance_pct,
        Budget.source_url,
    ]
    ncoa_code_col = []
    ncoa_desc_col = []
    state_name_col = []
    if _BUDGET_HAS_NCOA:
        ncoa_code_col = [NCOA.code.label("ncoa_code")]
        ncoa_desc_col = [NCOA.description.label("ncoa_description")]
    if _BUDGET_HAS_STATE:
        state_name_col = [State.name.label("state_name")]

    all_cols = select_cols + ncoa_code_col + ncoa_desc_col + state_name_col
    query = db.query(*all_cols).join(MDA, Budget.mda_id == MDA.id).join(
        FiscalYear, Budget.year_id == FiscalYear.id
    )

    if _BUDGET_HAS_NCOA:
        query = query.outerjoin(NCOA, Budget.ncoa_id == NCOA.id)
    if _BUDGET_HAS_STATE:
        query = query.outerjoin(State, Budget.state_id == State.id)

    # Filters
    if mda_id is not None:
        query = query.filter(Budget.mda_id == mda_id)
    if state_id is not None and _BUDGET_HAS_STATE:
        query = query.filter(Budget.state_id == state_id)
    if year is not None:
        query = query.filter(FiscalYear.year == year)
    if budget_type is not None and _BUDGET_HAS_TYPE:
        query = query.filter(Budget.budget_type == budget_type)

    return query


def _build_spending_query(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
):
    """Build a filtered query joining Spending -> MDA, with optional FiscalYear/State."""
    select_cols = [
        Spending.id.label("spending_id"),
        MDA.name.label("mda_name"),
        MDA.code.label("mda_code"),
        FiscalYear.year.label("fiscal_year"),
        Spending.beneficiary,
        Spending.purpose,
        Spending.amount,
        Spending.date,
        Spending.reference,
        Spending.latitude,
        Spending.longitude,
        Spending.source,
    ]

    query = db.query(*select_cols).join(MDA, Spending.mda_id == MDA.id)

    if _SPENDING_HAS_YEAR:
        query = query.outerjoin(FiscalYear, Spending.year_id == FiscalYear.id)
    else:
        # Replace fiscal_year with a null literal when column doesn't exist
        select_cols[3] = literal(None).label("fiscal_year")
        query = db.query(*select_cols).join(MDA, Spending.mda_id == MDA.id)

    if _SPENDING_HAS_STATE:
        query = query.outerjoin(State, Spending.state_id == State.id)

    if mda_id is not None:
        query = query.filter(Spending.mda_id == mda_id)
    if state_id is not None and _SPENDING_HAS_STATE:
        query = query.filter(Spending.state_id == state_id)
    if year is not None and _SPENDING_HAS_YEAR:
        query = query.filter(FiscalYear.year == year)
    if date_from is not None:
        query = query.filter(Spending.date >= date_from)
    if date_to is not None:
        query = query.filter(Spending.date <= date_to)
    if amount_min is not None:
        query = query.filter(Spending.amount >= amount_min)
    if amount_max is not None:
        query = query.filter(Spending.amount <= amount_max)

    return query


def _rows_to_csv(rows: list[dict], fieldnames: list[str]) -> str:
    """Convert a list of dicts to a CSV string."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return buf.getvalue()


def export_budget_csv(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    budget_type: Optional[str] = None,
) -> StreamingResponse:
    """Export filtered budget data as a CSV download."""
    dynamic_fields = ["budget_id", "mda_name", "mda_code", "fiscal_year"]
    if _BUDGET_HAS_NCOA:
        dynamic_fields += ["ncoa_code", "ncoa_description"]
    if _BUDGET_HAS_STATE:
        dynamic_fields.append("state_name")
    dynamic_fields += [
        "season", "approved", "revised", "estimated", "spent",
        "variance_pct", "source_url",
    ]
    query = _build_budget_query(db, mda_id, state_id, year, budget_type)
    rows = [dict(r._mapping) for r in query.all()]
    csv_text = _rows_to_csv(rows, dynamic_fields)

    filename = f"openspends_budgets_{year or 'all'}.csv"
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def export_spending_csv(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
) -> StreamingResponse:
    """Export filtered spending data as a CSV download."""
    FIELDNAMES = [
        "spending_id", "mda_name", "mda_code", "fiscal_year",
        "beneficiary", "purpose", "amount", "date", "reference",
        "latitude", "longitude", "source",
    ]
    query = _build_spending_query(db, mda_id, state_id, year, date_from, date_to, amount_min, amount_max)
    rows = [dict(r._mapping) for r in query.all()]
    csv_text = _rows_to_csv(rows, FIELDNAMES)

    filename = f"openspends_spending_{year or 'all'}.csv"
    return StreamingResponse(
        io.StringIO(csv_text),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def export_budget_json(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    budget_type: Optional[str] = None,
) -> StreamingResponse:
    """Export filtered budget data as a JSON download."""
    query = _build_budget_query(db, mda_id, state_id, year, budget_type)
    rows = [dict(r._mapping) for r in query.all()]
    for row in rows:
        for k, v in row.items():
            if isinstance(v, date):
                row[k] = v.isoformat()

    filename = f"openspends_budgets_{year or 'all'}.json"
    json_bytes = json.dumps({"data": rows, "total": len(rows)}, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_bytes.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def export_spending_json(
    db: Session,
    mda_id: Optional[int] = None,
    state_id: Optional[int] = None,
    year: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
) -> StreamingResponse:
    """Export filtered spending data as a JSON download."""
    query = _build_spending_query(db, mda_id, state_id, year, date_from, date_to, amount_min, amount_max)
    rows = [dict(r._mapping) for r in query.all()]
    for row in rows:
        for k, v in row.items():
            if isinstance(v, date):
                row[k] = v.isoformat()

    filename = f"openspends_spending_{year or 'all'}.json"
    json_bytes = json.dumps({"data": rows, "total": len(rows)}, indent=2, default=str)
    return StreamingResponse(
        io.BytesIO(json_bytes.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
