"""Pydantic schemas for API request/response validation."""

from datetime import date, datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


# ── States ──

class StateOut(BaseModel):
    id: int
    name: str
    code: str
    capital: Optional[str] = None
    region: Optional[str] = None

    class Config:
        from_attributes = True


# ── LGAs ──

class LGAOut(BaseModel):
    id: int
    state_id: int
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True


# ── MDAs ──

class MDAOut(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    level: Optional[str] = None
    state_id: Optional[int] = None
    lga_id: Optional[int] = None
    parent_id: Optional[int] = None
    ncoa_sector: Optional[str] = None

    class Config:
        from_attributes = True


class MDAListParams(BaseModel):
    level: Optional[Literal["fed", "state", "lga"]] = None
    state_id: Optional[int] = None
    ncoa_sector: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ── Budgets ──

class BudgetOut(BaseModel):
    id: int
    mda_id: int
    year_id: int
    season: str
    approved: Optional[float] = None
    revised: Optional[float] = None
    estimated: Optional[float] = None
    spent: Optional[float] = None
    variance_pct: Optional[float] = None
    source_url: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── Spending ──

class SpendingOut(BaseModel):
    id: int
    mda_id: int
    beneficiary: Optional[str] = None
    purpose: Optional[str] = None
    amount: float
    date: date
    reference: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class SpendingListParams(BaseModel):
    mda_id: Optional[int] = None
    state_id: Optional[int] = None
    amount_min: Optional[float] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ── Projects ──

class ProjectOut(BaseModel):
    id: int
    title: str
    mda_id: Optional[int] = None
    state_id: int
    lga_id: Optional[int] = None
    contractor: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    budget_allocated: Optional[float] = None
    spent: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectListParams(BaseModel):
    state_id: Optional[int] = None
    lga_id: Optional[int] = None
    status: Optional[str] = None
    mda_id: Optional[int] = None
    year: Optional[int] = None
    format: Optional[Literal["json", "geojson"]] = "json"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ── Analytics ──

class VarianceDataPoint(BaseModel):
    year: int
    mda_id: int
    mda_name: str
    budgeted: float
    spent: float
    variance_pct: float


class GeographicDataPoint(BaseModel):
    state_id: int
    state_name: str
    total_budgeted: float
    total_spent: float
    project_count: int


# ── Variance / Researcher Suite ──

class VarianceFlagItem(BaseModel):
    mda_id: int
    mda_name: str
    mda_code: Optional[str] = None
    year: Optional[int] = None
    allocated: float
    spent: float
    variance_amount: float
    variance_pct: float
    utilization_pct: float
    flag: str  # "over_utilization" | "under_utilization" | "on_track"
    budget_lines: int = 0
    spending_transactions: int = 0


class VarianceSummary(BaseModel):
    total_mdas: int = 0
    over_utilized: int = 0
    under_utilized: int = 0
    on_track: int = 0


class VarianceAnalysisResponse(BaseModel):
    data: list[VarianceFlagItem]
    total: int
    page: int
    page_size: int
    pages: int
    summary: VarianceSummary


class ExportFormatResponse(BaseModel):
    """Metadata describing available export formats."""
    formats: list[str] = ["csv", "json"]
    available_filters: list[str] = [
        "mda_id", "state_id", "year", "date_from", "date_to",
        "amount_min", "amount_max", "ncoa_code", "budget_type",
    ]


# ── Geocoding ──

class GeocodeRequest(BaseModel):
    address: str
    state: Optional[str] = None
    lga: Optional[str] = None


class GeocodeResponse(BaseModel):
    latitude: float
    longitude: float
    source: str


# ── Pagination ──

class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    pages: int


# ── Health ──

class HealthResponse(BaseModel):
    status: str
    version: str
