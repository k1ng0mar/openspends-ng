"""SQLAlchemy ORM models for OpenSpends NG."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, Text,
    ForeignKey, Index, UniqueConstraint, Boolean, JSON
)
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.core.database import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(10), nullable=False, unique=True)  # e.g., "LA", "FC"
    capital = Column(String(100))
    region = Column(String(50))  # "north-west", "south-east", etc.

    lgas = relationship("LGA", back_populates="state")
    mdas = relationship("MDA", back_populates="state")


class LGA(Base):
    __tablename__ = "lgas"

    id = Column(Integer, primary_key=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(20))

    state = relationship("State", back_populates="lgas")
    projects = relationship("Project", back_populates="lga")

    __table_args__ = (
        UniqueConstraint("state_id", "name"),
    )


class MDA(Base):
    __tablename__ = "mdas"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    code = Column(String(20), unique=True)  # e.g., "FED-FINANCE"
    level = Column(String(10), nullable=False)  # "fed", "state", "lga"
    state_id = Column(Integer, ForeignKey("states.id"))
    lga_id = Column(Integer, ForeignKey("lgas.id"))
    parent_id = Column(Integer, ForeignKey("mdas.id"))
    ncoa_sector = Column(String(10))  # e.g., "07" (Health)

    state = relationship("State", back_populates="mdas")
    budgets = relationship("Budget", back_populates="mda")
    spending = relationship("Spending", back_populates="mda")
    projects = relationship("Project", back_populates="mda")

    __table_args__ = (
        Index("idx_mda_level", "level"),
        Index("idx_mda_state", "state_id"),
    )


class FiscalYear(Base):
    __tablename__ = "fiscal_years"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False, unique=True)
    is_current = Column(Boolean, default=False)


class NCOA(Base):
    __tablename__ = "ncoa"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)  # e.g., "21010101"
    description = Column(String(300))
    category = Column(String(100))  # "Personnel Cost"
    chapter = Column(String(100))   # "21"
    group_name = Column(String(100))  # "2101"


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    mda_id = Column(Integer, ForeignKey("mdas.id"), nullable=False)
    year_id = Column(Integer, ForeignKey("fiscal_years.id"), nullable=False)
    season = Column(String(10), nullable=False)  # "budget", "q1", "q2", "q3", "q4"
    approved = Column(Float)
    revised = Column(Float)
    estimated = Column(Float)
    spent = Column(Float)  # Aggregated from spending table
    variance_pct = Column(Float)
    source_url = Column(String(500))  # Link to PDF
    updated_at = Column(DateTime, default=datetime.utcnow)

    mda = relationship("MDA", back_populates="budgets")

    __table_args__ = (
        Index("idx_budget_mda_year", "mda_id", "year_id"),
        UniqueConstraint("mda_id", "year_id", "season"),
    )


class Spending(Base):
    __tablename__ = "spending"

    id = Column(Integer, primary_key=True)
    mda_id = Column(Integer, ForeignKey("mdas.id"), nullable=False)
    beneficiary = Column(String(300))
    purpose = Column(Text)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    reference = Column(String(100))
    location_id = Column(String(50))  # FK to geolocation_cache
    latitude = Column(Float)  # Denormalized for quick map queries
    longitude = Column(Float)
    source = Column(String(50))  # "govspend", "open_treasury", "manual"
    source_hash = Column(String(64), index=True)  # SHA-256 hash for dedup
    created_at = Column(DateTime, default=datetime.utcnow)

    mda = relationship("MDA", back_populates="spending")

    __table_args__ = (
        Index("idx_spending_date_mda", "date", "mda_id"),
        Index("idx_spending_amount", "amount"),
        Index("idx_spending_source_hash", "source_hash"),
    )


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    mda_id = Column(Integer, ForeignKey("mdas.id"))
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    lga_id = Column(Integer, ForeignKey("lgas.id"))
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    contractor = Column(String(300))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, abandoned
    budget_allocated = Column(Float)
    spent = Column(Float, default=0)
    geolocation = Column(Geometry("POINT", srid=4326))  # PostGIS
    photos = Column(Text)  # JSON array of URLs
    source = Column(String(50))  # "tracka", "bpp", "icpc", "manual"
    source_hash = Column(String(64), index=True)  # SHA-256 hash for dedup
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    mda = relationship("MDA", back_populates="projects")
    lga = relationship("LGA", back_populates="projects")

    __table_args__ = (
        Index("idx_project_state_status", "state_id", "status"),
        Index("idx_project_mda", "mda_id"),
        Index("idx_project_source_hash", "source_hash"),
    )


class GeolocationCache(Base):
    __tablename__ = "geolocation_cache"

    id = Column(String(50), primary_key=True)  # Hash of address
    address = Column(String(300))
    state = Column(String(100))
    lga = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source = Column(String(50))  # "tracka", "nominatim", "google", "manual"
    created_at = Column(DateTime, default=datetime.utcnow)


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True)
    ocid = Column(String(100), unique=True)  # OCDS ID
    title = Column(String(500))
    mda_id = Column(Integer, ForeignKey("mdas.id"))
    amount = Column(Float)
    status = Column(String(50))
    award_date = Column(Date)
    supplier = Column(String(300))
    source_data = Column(Text)  # Raw OCDS JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_contract_ocid", "ocid"),
    )


# ── Pipeline Infrastructure Models ──

class PipelineRun(Base):
    """Tracks each pipeline execution for monitoring and audit."""
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # "govspend", "pdf_parser", "bpp", "icpc"
    status = Column(String(20), nullable=False, default="pending")  # pending, running, success, failed, partial
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime)
    records_found = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)  # Duplicates
    error_message = Column(Text)
    details = Column(JSON)  # Extra context: page counts, file names, etc.

    __table_args__ = (
        Index("idx_pipeline_source_status", "source", "status"),
        Index("idx_pipeline_started", "started_at"),
    )


class DataSourceRegistry(Base):
    """Registry of known external data sources and their configuration."""
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # "govspend", "tracka", "bpp"
    display_name = Column(String(200))
    base_url = Column(String(500))
    source_type = Column(String(20))  # "api", "scraper", "pdf", "manual"
    is_active = Column(Boolean, default=True)
    schedule = Column(String(100))  # Cron-like expression or interval description
    last_success_at = Column(DateTime)
    last_run_at = Column(DateTime)
    run_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    config = Column(JSON)  # Source-specific configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
