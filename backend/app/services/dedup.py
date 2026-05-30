"""
OpenSpends NG — Data Deduplication & Cleaning Service

Provides hash-based dedup, fuzzy title matching, and data normalization
for projects and spending records before DB insertion.
"""

import hashlib
import logging
import re
from datetime import datetime, date
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Project, Spending, PipelineRun

logger = logging.getLogger(__name__)


# ── Hashing for Deduplication ──

def _normalize_str(s: Optional[str]) -> str:
    """Lowercase, strip whitespace, collapse repeated spaces."""
    if not s:
        return ""
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def _clean_naira(amount: Optional[float]) -> Optional[float]:
    """Normalize Naira amounts: round to 2dp, reject obvious garbage."""
    if amount is None:
        return None
    if amount < 0 or amount > 1e15:  # 1 quadrillion Naira is unreasonable
        return None
    return round(amount, 2)


def compute_spending_hash(
    date_str: str,
    mda_name: str,
    beneficiary: str,
    amount: float,
    reference: str = "",
) -> str:
    """
    Deterministic SHA-256 hash for a spending record.
    Used to detect duplicates across scraper runs.
    """
    parts = [
        _normalize_str(date_str),
        _normalize_str(mda_name),
        _normalize_str(beneficiary),
        f"{_clean_naira(amount):.2f}" if amount else "",
        _normalize_str(reference),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def compute_project_hash(
    title: str,
    state_code: str,
    mda_name: str,
    budget_allocated: float = 0,
    start_date: str = "",
) -> str:
    """
    Deterministic SHA-256 hash for a project record.
    Title is fuzzy-normalized before hashing.
    """
    fuzzy_title = _normalize_str(title)
    # Remove common punctuation that varies across sources
    fuzzy_title = re.sub(r"[,.;:()'\"-]", "", fuzzy_title)

    parts = [
        fuzzy_title,
        _normalize_str(state_code),
        _normalize_str(mda_name),
        f"{_clean_naira(budget_allocated):.2f}" if budget_allocated else "",
        _normalize_str(start_date),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ── Fuzzy Matching ──

def _token_jaccard(a: str, b: str) -> float:
    """Jaccard similarity between two strings' token sets."""
    tokens_a = set(_normalize_str(a).split())
    tokens_b = set(_normalize_str(b).split())
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def is_duplicate_project(
    db: Session,
    title: str,
    state_code: str,
    mda_name: str,
    budget_allocated: float = 0,
    start_date: str = "",
    hash_threshold: float = 0.0,  # Exact hash match
    fuzzy_threshold: float = 0.85,  # Token Jaccard similarity
) -> Optional[Project]:
    """
    Check if a project already exists using:
    1. Exact hash match (fast path)
    2. Fuzzy title + same state/mda (slow path)

    Returns the existing Project if found, None otherwise.
    """
    from app.models import State

    # Fast path: exact hash
    source_hash = compute_project_hash(title, state_code, mda_name, budget_allocated, start_date)
    existing = db.query(Project).filter_by(source_hash=source_hash).first()
    if existing:
        logger.debug(f"Hash match for project: {title[:60]}")
        return existing

    # Slow path: fuzzy title match within same state + mda
    state = db.query(State).filter_by(code=state_code).first()
    if not state:
        return None

    from app.models import MDA
    mda = db.query(MDA).filter(func.lower(MDA.name) == _normalize_str(mda_name)).first()
    if not mda:
        return None

    candidates = (
        db.query(Project)
        .filter(Project.state_id == state.id, Project.mda_id == mda.id)
        .all()
    )

    for candidate in candidates:
        similarity = _token_jaccard(title, candidate.title)
        if similarity >= fuzzy_threshold:
            logger.debug(
                f"Fuzzy match ({similarity:.2f}) for project: {title[:60]} → {candidate.title[:60]}"
            )
            return candidate

    return None


def is_duplicate_spending(
    db: Session,
    date_str: str,
    mda_name: str,
    beneficiary: str,
    amount: float,
    reference: str = "",
) -> Optional[Spending]:
    """
    Check if a spending record already exists using exact hash match.
    Spending records are considered duplicates if they have the same
    date, beneficiary, amount, and reference.
    """
    source_hash = compute_spending_hash(date_str, mda_name, beneficiary, amount, reference)
    existing = db.query(Spending).filter_by(source_hash=source_hash).first()
    if existing:
        logger.debug(f"Hash match for spending: {beneficiary[:60]} ({date_str})")
    return existing


# ── Data Cleaning ──

def clean_project_record(record: dict) -> dict:
    """Normalize and validate a raw project dict before insertion."""
    cleaned = dict(record)

    # Normalize title
    title = cleaned.get("title", "")
    if title:
        title = re.sub(r"\s+", " ", title).strip()
        title = title[:500]  # Truncate to column limit
        cleaned["title"] = title

    # Normalize status
    valid_statuses = {"not_started", "in_progress", "completed", "abandoned"}
    status = _normalize_str(cleaned.get("status", ""))
    if status not in valid_statuses:
        # Map common variations
        status_map = {
            "ongoing": "in_progress",
            "in progress": "in_progress",
            "done": "completed",
            "finished": "completed",
            "cancelled": "abandoned",
            "abandoned": "abandoned",
            "not started": "not_started",
        }
        cleaned["status"] = status_map.get(status, "not_started")

    # Clean amounts
    cleaned["budget_allocated"] = _clean_naira(cleaned.get("budget_allocated"))
    cleaned["spent"] = _clean_naira(cleaned.get("spent", 0)) or 0

    # Normalize dates
    for field in ("start_date", "end_date"):
        val = cleaned.get(field)
        if isinstance(val, str) and not val.strip():
            cleaned[field] = None

    # Generate source hash if not present
    if not cleaned.get("source_hash"):
        cleaned["source_hash"] = compute_project_hash(
            title=cleaned.get("title", ""),
            state_code=cleaned.get("state_code", ""),
            mda_name=cleaned.get("mda_name", ""),
            budget_allocated=cleaned.get("budget_allocated", 0),
            start_date=str(cleaned.get("start_date", "")),
        )

    # Normalize source
    valid_sources = {"tracka", "bpp", "icpc", "manual", "govspend", "open_treasury"}
    source = _normalize_str(cleaned.get("source", ""))
    if source not in valid_sources:
        cleaned["source"] = "manual"

    return cleaned


def clean_spending_record(record: dict) -> dict:
    """Normalize and validate a raw spending dict before insertion."""
    cleaned = dict(record)

    # Normalize beneficiary
    beneficiary = cleaned.get("beneficiary", "")
    if beneficiary:
        beneficiary = re.sub(r"\s+", " ", beneficiary).strip()
        beneficiary = beneficiary[:300]
        cleaned["beneficiary"] = beneficiary

    # Clean amount
    cleaned["amount"] = _clean_naira(cleaned.get("amount")) or 0

    # Validate date
    if not cleaned.get("date"):
        cleaned["date"] = str(date.today())

    # Generate source hash if not present
    if not cleaned.get("source_hash"):
        cleaned["source_hash"] = compute_spending_hash(
            date_str=str(cleaned.get("date", "")),
            mda_name=cleaned.get("mda_name", ""),
            beneficiary=cleaned.get("beneficiary", ""),
            amount=cleaned.get("amount", 0),
            reference=cleaned.get("reference", ""),
        )

    # Normalize source
    valid_sources = {"govspend", "open_treasury", "manual", "bpp", "icpc"}
    source = _normalize_str(cleaned.get("source", ""))
    if source not in valid_sources:
        cleaned["source"] = "manual"

    return cleaned


# ── Pipeline Run Tracking ──

def start_pipeline_run(db: Session, source: str) -> PipelineRun:
    """Create a new pipeline run record."""
    run = PipelineRun(source=source, status="running", started_at=datetime.utcnow())
    db.add(run)
    db.commit()
    db.refresh(run)
    logger.info(f"Pipeline run started: {source} (id={run.id})")
    return run


def finish_pipeline_run(
    db: Session,
    run_id: int,
    status: str = "success",
    records_found: int = 0,
    records_inserted: int = 0,
    records_updated: int = 0,
    records_skipped: int = 0,
    error_message: Optional[str] = None,
    details: Optional[dict] = None,
):
    """Update a pipeline run with completion data."""
    run = db.query(PipelineRun).filter_by(id=run_id).first()
    if not run:
        logger.warning(f"Pipeline run {run_id} not found")
        return

    run.status = status
    run.finished_at = datetime.utcnow()
    run.records_found = records_found
    run.records_inserted = records_inserted
    run.records_updated = records_updated
    run.records_skipped = records_skipped
    run.error_message = error_message
    if details:
        run.details = details

    db.commit()

    duration = (run.finished_at - run.started_at).total_seconds() if run.finished_at else 0
    logger.info(
        f"Pipeline run finished: {run.source} (id={run.id}) "
        f"status={status} found={records_found} inserted={records_inserted} "
        f"skipped={records_skipped} updated={records_updated} "
        f"duration={duration:.1f}s"
    )


def get_pipeline_stats(db: Session, source: str = None, limit: int = 50) -> list[dict]:
    """Get recent pipeline run statistics."""
    query = db.query(PipelineRun)
    if source:
        query = query.filter_by(source=source)
    runs = query.order_by(PipelineRun.started_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "source": r.source,
            "status": r.status,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "records_found": r.records_found,
            "records_inserted": r.records_inserted,
            "records_updated": r.records_updated,
            "records_skipped": r.records_skipped,
            "error_message": r.error_message,
            "details": r.details,
        }
        for r in runs
    ]
