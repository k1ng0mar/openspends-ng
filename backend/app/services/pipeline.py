"""
OpenSpends NG — Data Ingestion Pipeline Orchestrator

Orchestrates the full data flow:
1. Scrape GovSpend (or other sources)
2. Parse PDF budgets
3. Clean + deduplicate records
4. Insert into database
5. Track pipeline health via PipelineRun records

Uses APScheduler for periodic execution, or can be triggered manually
via the API endpoint.
"""

import logging
import re
from datetime import datetime, date, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models import (
    Spending, Project, MDA, State, Budget, FiscalYear, PipelineRun,
)
from app.services.dedup import (
    start_pipeline_run, finish_pipeline_run,
    clean_spending_record, clean_project_record,
    is_duplicate_spending, is_duplicate_project,
    compute_spending_hash, compute_project_hash,
)

logger = logging.getLogger(__name__)

# ── MDA/State Resolution Helpers ──

def _resolve_mda(db: Session, mda_name: str, level: str = "fed") -> Optional[int]:
    """Find or create an MDA by name, returning its ID."""
    if not mda_name:
        return None

    normalized = mda_name.strip().lower()
    mda = db.query(MDA).filter(func.lower(MDA.name) == normalized).first()
    if mda:
        return mda.id

    # Create a new MDA — use a generated code
    code = re.sub(r"[^a-z0-9]+", "-", normalized)[:20].strip("-")
    existing_code = db.query(MDA).filter_by(code=code).first()
    if existing_code:
        code = f"{code}-{db.query(MDA).count() + 1}"

    mda = MDA(name=mda_name.strip(), code=code, level=level)
    db.add(mda)
    db.flush()
    logger.info(f"Created new MDA: {mda_name}")
    return mda.id


def _resolve_state(db: Session, state_code: Optional[str] = None, state_name: Optional[str] = None) -> Optional[int]:
    """Find a state by code or name, returning its ID."""
    if state_code:
        state = db.query(State).filter_by(code=state_code.upper().strip()).first()
        if state:
            return state.id
    if state_name:
        state = db.query(State).filter(func.lower(State.name) == state_name.lower().strip()).first()
        if state:
            return state.id
    return None


def _resolve_fiscal_year(db: Session, year: int) -> Optional[int]:
    """Find or create a fiscal year, returning its ID."""
    fy = db.query(FiscalYear).filter_by(year=year).first()
    if fy:
        return fy.id
    fy = FiscalYear(year=year, is_current=(year >= date.today().year))
    db.add(fy)
    db.flush()
    return fy.id


# ── Spending Ingestion ──

def ingest_spending_records(
    db: Session,
    records: list[dict],
    source: str = "govspend",
    pipeline_run_id: int = None,
) -> dict:
    """
    Ingest cleaned spending records with deduplication.

    Each record dict should have:
        date, mda_name, beneficiary, amount, description, payment_ref, source

    Returns summary dict with counts.
    """
    inserted = 0
    updated = 0
    skipped = 0

    for raw in records:
        try:
            # Clean
            rec = clean_spending_record(raw)
            if not rec.get("amount", 0) > 0:
                skipped += 1
                continue

            # Resolve MDA
            mda_id = _resolve_mda(db, rec.get("mda_name", ""))
            if not mda_id:
                skipped += 1
                continue

            # Handle date
            rec_date = rec.get("date")
            if isinstance(rec_date, str):
                try:
                    rec_date = date.fromisoformat(rec_date)
                except ValueError:
                    rec_date = date.today()

            # Dedup check
            existing = is_duplicate_spending(
                db,
                date_str=str(rec_date),
                mda_name=rec.get("mda_name", ""),
                beneficiary=rec.get("beneficiary", ""),
                amount=rec["amount"],
                reference=rec.get("reference", ""),
            )

            if existing:
                # Update if amount changed significantly
                if abs(existing.amount - rec["amount"]) > 0.01:
                    existing.amount = rec["amount"]
                    existing.beneficiary = rec.get("beneficiary", existing.beneficiary)
                    updated += 1
                else:
                    skipped += 1
                continue

            # Insert
            spending = Spending(
                mda_id=mda_id,
                beneficiary=rec.get("beneficiary", ""),
                purpose=rec.get("description", ""),
                amount=rec["amount"],
                date=rec_date,
                reference=rec.get("reference", ""),
                source=rec.get("source", source),
                source_hash=rec["source_hash"],
            )
            db.add(spending)
            inserted += 1

        except Exception as e:
            logger.error(f"Error ingesting spending record: {e}")
            skipped += 1

    db.commit()
    logger.info(
        f"Spending ingestion complete: inserted={inserted} updated={updated} skipped={skipped}"
    )
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


# ── Project Ingestion ──

def ingest_project_records(
    db: Session,
    records: list[dict],
    source: str = "tracka",
    pipeline_run_id: int = None,
) -> dict:
    """
    Ingest cleaned project records with deduplication.

    Each record dict should have:
        title, state_code, mda_name, contractor, start_date, end_date,
        status, budget_allocated, spent, latitude, longitude, source

    Returns summary dict with counts.
    """
    inserted = 0
    updated = 0
    skipped = 0
    from geoalchemy2.elements import WKTElement

    for raw in records:
        try:
            # Clean
            rec = clean_project_record(raw)
            if not rec.get("title"):
                skipped += 1
                continue

            # Resolve required foreign keys
            state_id = _resolve_state(db, state_code=rec.get("state_code"), state_name=rec.get("state_name"))
            if not state_id:
                logger.warning(f"Cannot resolve state for project: {rec['title'][:60]}")
                skipped += 1
                continue

            mda_id = _resolve_mda(db, rec.get("mda_name", ""))

            # Handle dates
            start_date = rec.get("start_date")
            end_date = rec.get("end_date")
            if isinstance(start_date, str) and start_date:
                try:
                    start_date = date.fromisoformat(start_date)
                except ValueError:
                    start_date = None
            if isinstance(end_date, str) and end_date:
                try:
                    end_date = date.fromisoformat(end_date)
                except ValueError:
                    end_date = None

            # Geolocation
            geolocation = None
            lat = rec.get("latitude")
            lng = rec.get("longitude")
            if lat and lng:
                try:
                    geolocation = WKTElement(f"POINT({float(lng)} {float(lat)})", srid=4326)
                except (ValueError, TypeError):
                    geolocation = None

            # Dedup check
            existing = is_duplicate_project(
                db,
                title=rec["title"],
                state_code=rec.get("state_code", ""),
                mda_name=rec.get("mda_name", ""),
                budget_allocated=rec.get("budget_allocated", 0),
                start_date=str(rec.get("start_date", "")),
            )

            if existing:
                changed = False
                # Update mutable fields
                if rec.get("budget_allocated") and existing.budget_allocated != rec["budget_allocated"]:
                    existing.budget_allocated = rec["budget_allocated"]
                    changed = True
                if rec.get("spent") and existing.spent != rec["spent"]:
                    existing.spent = rec["spent"]
                    changed = True
                if rec.get("status") and existing.status != rec["status"]:
                    existing.status = rec["status"]
                    changed = True
                if geolocation and not existing.geolocation:
                    existing.geolocation = geolocation
                    changed = True
                if changed:
                    existing.updated_at = datetime.utcnow()
                    updated += 1
                else:
                    skipped += 1
                continue

            # Insert
            project = Project(
                title=rec["title"],
                mda_id=mda_id,
                state_id=state_id,
                contractor=rec.get("contractor", ""),
                start_date=start_date,
                end_date=end_date,
                status=rec.get("status", "not_started"),
                budget_allocated=rec.get("budget_allocated"),
                spent=rec.get("spent", 0),
                geolocation=geolocation,
                source=rec.get("source", source),
                source_hash=rec["source_hash"],
            )
            db.add(project)
            inserted += 1

        except Exception as e:
            logger.error(f"Error ingesting project record: {e}")
            skipped += 1

    db.commit()
    logger.info(
        f"Project ingestion complete: inserted={inserted} updated={updated} skipped={skipped}"
    )
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


# ── Pipeline Task Runners ──

def run_govspend_pipeline(db: Session = None) -> dict:
    """
    Execute the full GovSpend scraping + ingestion pipeline.
    Can be called from API endpoint or scheduler.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    run = start_pipeline_run(db, "govspend")
    result = {"source": "govspend", "run_id": run.id, "status": "success"}

    try:
        logger.info("Starting GovSpend pipeline...")

        # Import and run scraper
        from app.services.govspend_scraper import scrape_govspend
        payments = scrape_govspend(max_pages=3)

        if not payments:
            logger.warning("GovSpend scraper returned no records")
            finish_pipeline_run(
                db, run.id, status="success",
                records_found=0, details={"message": "No records found"},
            )
            result["message"] = "No records found"
            return result

        # Ingest with dedup
        ingest_result = ingest_spending_records(db, payments, source="govspend")
        result.update(ingest_result)

        finish_pipeline_run(
            db, run.id, status="success",
            records_found=len(payments),
            records_inserted=ingest_result["inserted"],
            records_updated=ingest_result["updated"],
            records_skipped=ingest_result["skipped"],
        )

    except Exception as e:
        logger.error(f"GovSpend pipeline failed: {e}")
        finish_pipeline_run(db, run.id, status="failed", error_message=str(e))
        result["status"] = "failed"
        result["error"] = str(e)
    finally:
        if own_session:
            db.close()

    return result


def run_budget_pdf_pipeline(pdf_path: str, db: Session = None) -> dict:
    """
    Execute the PDF budget parsing + ingestion pipeline.
    """
    own_session = db is None
    if own_session:
        db = SessionLocal()

    run = start_pipeline_run(db, "pdf_parser")
    result = {"source": "pdf_parser", "run_id": run.id, "status": "success", "file": pdf_path}

    try:
        logger.info(f"Starting PDF pipeline for: {pdf_path}")

        from app.services.pdf_parser import parse_budget_pdf
        parsed = parse_budget_pdf(pdf_path)

        appropriation_records = parsed.get("appropriation_records", [])
        result["metadata"] = parsed.get("metadata", {})
        result["tables_found"] = len(parsed.get("raw_tables", []))

        if appropriation_records:
            # Convert appropriation records to spending-like records for insertion
            # In a real system you'd have a separate budget ingestion path
            result["appropriation_records"] = len(appropriation_records)
            logger.info(f"Parsed {len(appropriation_records)} budget appropriation records")

        # For now, store the parsed data; budget table ingestion would
        # need a dedicated method
        finish_pipeline_run(
            db, run.id, status="success",
            records_found=len(appropriation_records),
            records_inserted=0,
            details={
                "file": pdf_path,
                "tables": len(parsed.get("raw_tables", [])),
                "records": len(appropriation_records),
            },
        )

    except Exception as e:
        logger.error(f"PDF pipeline failed: {e}")
        finish_pipeline_run(db, run.id, status="failed", error_message=str(e))
        result["status"] = "failed"
        result["error"] = str(e)
    finally:
        if own_session:
            db.close()

    return result


def run_full_pipeline(db: Session = None) -> dict:
    """Run all data source pipelines sequentially."""
    own_session = db is None
    if own_session:
        db = SessionLocal()

    results = {}

    # GovSpend
    try:
        govspend_result = run_govspend_pipeline(db=db)
        results["govspend"] = govspend_result
    except Exception as e:
        results["govspend"] = {"status": "failed", "error": str(e)}

    if own_session:
        db.close()

    return results
