"""
OpenSpends NG — Seed Data Script

Populates the database with:
- 36 Nigerian states + FCT
- Sample federal MDAs
- Fiscal years 2020-2026
- NCOA classification codes
- Sample budget records

Run: python scripts/seed.py --db-url postgresql+psycopg://user:pass@host/db
"""

import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import (
    State, MDA, FiscalYear, NCOA, Budget, Project
)


# ── Seed Data ──

STATES = [
    ("Abia", "AB", "Umuahia", "south-east"),
    ("Adamawa", "AD", "Yola", "north-east"),
    ("Akwa Ibom", "AK", "Uyo", "south-south"),
    ("Anambra", "AN", "Awka", "south-east"),
    ("Bauchi", "BA", "Bauchi", "north-east"),
    ("Bayelsa", "BY", "Yenagoa", "south-south"),
    ("Benue", "BE", "Makurdi", "north-central"),
    ("Borno", "BO", "Maiduguri", "north-east"),
    ("Cross River", "CR", "Calabar", "south-south"),
    ("Delta", "DE", "Asaba", "south-south"),
    ("Ebonyi", "EB", "Abakaliki", "south-east"),
    ("Edo", "ED", "Benin City", "south-south"),
    ("Ekiti", "EK", "Ado-Ekiti", "south-west"),
    ("Enugu", "EN", "Enugu", "south-east"),
    ("Gombe", "GO", "Gombe", "north-east"),
    ("Imo", "IM", "Owerri", "south-east"),
    ("Jigawa", "JI", "Dutse", "north-west"),
    ("Kaduna", "KD", "Kaduna", "north-west"),
    ("Kano", "KN", "Kano", "north-west"),
    ("Katsina", "KT", "Katsina", "north-west"),
    ("Kebbi", "KE", "Birnin Kebbi", "north-west"),
    ("Kogi", "KO", "Lokoja", "north-central"),
    ("Kwara", "KW", "Ilorin", "north-central"),
    ("Lagos", "LA", "Ikeja", "south-west"),
    ("Nasarawa", "NA", "Lafia", "north-central"),
    ("Niger", "NI", "Minna", "north-central"),
    ("Ogun", "OG", "Abeokuta", "south-west"),
    ("Ondo", "ON", "Akure", "south-west"),
    ("Osun", "OS", "Oshogbo", "south-west"),
    ("Oyo", "OY", "Ibadan", "south-west"),
    ("Plateau", "PL", "Jos", "north-central"),
    ("Rivers", "RI", "Port Harcourt", "south-south"),
    ("Sokoto", "SO", "Sokoto", "north-west"),
    ("Taraba", "TA", "Jalingo", "north-east"),
    ("Zamfara", "ZA", "Gusau", "north-west"),
    ("FCT Abuja", "FC", "Abuja", "north-central"),
]

FEDERAL_MDAS = [
    ("Federal Ministry of Finance", "FED-FINANCE", "01"),
    ("Federal Ministry of Health", "FED-HEALTH", "07"),
    ("Federal Ministry of Education", "FED-EDUCATION", "09"),
    ("Federal Ministry of Defence", "FED-DEFENCE", "02"),
    ("Federal Ministry of Works & Housing", "FED-WORKS", "06"),
    ("Federal Ministry of Agriculture", "FED-AGRIC", "04"),
    ("Federal Ministry of Transportation", "FED-TRANSPORT", "04"),
    ("Federal Ministry of Power", "FED-POWER", "04"),
    ("Federal Ministry of Water Resources", "FED-WATER", "06"),
    ("Budget Office of the Federation", "BOF", "01"),
    ("Office of the Accountant General", "OAGF", "01"),
    ("Federal Inland Revenue Service", "FIRS", "01"),
]

NCOA_CODES = [
    ("2", "EXPENDITURE", "Expenditure"),
    ("21", "PERSONNEL COST", "Personnel Cost"),
    ("2101", "Salaries and Wages", "Salaries and Wages"),
    ("2102", "Allowances and Social Contribution", "Allowances"),
    ("22", "OTHER RECURRENT COSTS", "Overhead Cost"),
    ("2202", "Overhead Cost", "Overhead Cost"),
    ("220201", "Travel & Transport", "Travel"),
    ("23", "CAPITAL EXPENDITURE", "Capital Expenditure"),
    ("2301", "Fixed Assets", "Fixed Assets"),
    ("230101", "Buildings", "Buildings"),
    ("230102", "Vehicles", "Vehicles"),
    ("230103", "Equipment & Machinery", "Equipment"),
    ("230104", "Infrastructure", "Infrastructure"),
]

FISCAL_YEARS = [
    (2020, False),
    (2021, False),
    (2022, False),
    (2023, False),
    (2024, True),
    (2025, True),
    (2026, True),
]

SAMPLE_BUDGETS = [
    # (mda_name, year, season, approved, spent)
    ("Federal Ministry of Finance", 2024, "budget", 4_500_000_000_000.0, 3_200_000_000_000.0),
    ("Federal Ministry of Finance", 2025, "budget", 5_200_000_000_000.0, 4_100_000_000_000.0),
    ("Federal Ministry of Health", 2024, "budget", 1_800_000_000_000.0, 1_500_000_000_000.0),
    ("Federal Ministry of Health", 2025, "budget", 2_100_000_000_000.0, 1_750_000_000_000.0),
    ("Federal Ministry of Education", 2024, "budget", 1_200_000_000_000.0, 980_000_000_000.0),
    ("Federal Ministry of Education", 2025, "budget", 1_450_000_000_000.0, 1_100_000_000_000.0),
    ("Federal Ministry of Defence", 2024, "budget", 950_000_000_000.0, 870_000_000_000.0),
    ("Federal Ministry of Works & Housing", 2024, "budget", 780_000_000_000.0, 620_000_000_000.0),
    ("Federal Ministry of Works & Housing", 2025, "budget", 1_100_000_000_000.0, 850_000_000_000.0),
    ("Federal Ministry of Agriculture", 2024, "budget", 420_000_000_000.0, 350_000_000_000.0),
]

SAMPLE_PROJECTS = [
    # (title, mda_name, state_code, contractor, start, end, status, allocated, spent, lat, lng)
    ("Abuja-Kano Expressway Phase 1", "Federal Ministry of Transportation", "FC", "Buildwell Ltd", "2024-01-15", "2026-12-31", "in_progress", 450_000_000_000.0, 180_000_000_000.0, 9.0765, 7.3986),
    ("Lagos-Ibadan Expressway Rehabilitation", "Federal Ministry of Works & Housing", "LA", "Reynolds Construction", "2023-06-01", "2025-06-01", "completed", 210_000_000_000.0, 205_000_000_000.0, 6.5244, 3.3792),
    ("Abuja Metro Rail Extension", "Federal Ministry of Transportation", "FC", "CCCC Nigeria", "2024-03-01", "2027-03-01", "in_progress", 320_000_000_000.0, 85_000_000_000.0, 9.0579, 7.4951),
    ("National Health Insurance Scheme Upgrade", "Federal Ministry of Health", "FC", "HealthTech NG", "2024-07-01", "2025-12-31", "in_progress", 85_000_000_000.0, 42_000_000_000.0, 9.0765, 7.3986),
    ("Universal Basic Education Digital Labs", "Federal Ministry of Education", "FC", "EduTech Africa", "2024-09-01", "2026-06-30", "in_progress", 120_000_000_000.0, 35_000_000_000.0, 9.0765, 7.3986),
    ("Kano Water Supply Rehabilitation", "Federal Ministry of Water Resources", "KN", "Water Works Ltd", "2023-01-01", "2025-12-31", "in_progress", 65_000_000_000.0, 48_000_000_000.0, 12.0022, 8.5925),
    ("Mambilla Hydroelectric Dam", "Federal Ministry of Power", "TA", "Sinohydro", "2020-01-01", "2028-12-31", "in_progress", 3_600_000_000_000.0, 1_200_000_000_000.0, 6.7833, 11.2833),
]


def seed(database_url: str):
    """Populate database with seed data."""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # ── States ──
        for name, code, capital, region in STATES:
            if not session.query(State).filter_by(code=code).first():
                session.add(State(name=name, code=code, capital=capital, region=region))
        session.flush()
        print(f"Seeded {len(STATES)} states")

        # ── MDAs ──
        for name, code, ncoa_sector in FEDERAL_MDAS:
            if not session.query(MDA).filter_by(code=code).first():
                session.add(MDA(name=name, code=code, level="fed", ncoa_sector=ncoa_sector))
        session.flush()
        print(f"Seeded {len(FEDERAL_MDAs)} federal MDAs")

        # ── Fiscal Years ──
        for year, is_current in FISCAL_YEARS:
            if not session.query(FiscalYear).filter_by(year=year).first():
                session.add(FiscalYear(year=year, is_current=is_current))
        session.flush()

        # Build lookups
        year_map = {y.year: y.id for y in session.query(FiscalYear).all()}
        mda_map = {m.name: m.id for m in session.query(MDA).all()}
        print(f"Seeded {len(FISCAL_YEARS)} fiscal years")

        # ── NCOA ──
        for code, category, description in NCOA_CODES:
            if not session.query(NCOA).filter_by(code=code).first():
                session.add(NCOA(code=code, category=category, description=description, chapter=code[:2]))
        session.flush()
        print(f"Seeded {len(NCOA_CODES)} NCOA codes")

        # ── Budgets ──
        bcount = 0
        for mda_name, year, season, approved, spent in SAMPLE_BUDGETS:
            mda_id = mda_map.get(mda_name)
            year_id = year_map.get(year)
            if mda_id and year_id:
                existing = session.query(Budget).filter_by(mda_id=mda_id, year_id=year_id, season=season).first()
                if not existing:
                    b = Budget(
                        mda_id=mda_id, year_id=year_id, season=season,
                        approved=approved, spent=spent,
                        source_url="https://budgetoffice.gov.ng",
                        updated_at=date.today(),
                    )
                    session.add(b)
                    bcount += 1
        session.flush()
        print(f"Seeded {bcount} budget records")

        # ── Projects ──
        state_map = {s.code: s.id for s in session.query(State).all()}
        pcount = 0
        for title, mda_name, state_code, contractor, start, end, status, allocated, spent, lat, lng in SAMPLE_PROJECTS:
            mda_id = mda_map.get(mda_name)
            state_id = state_map.get(state_code)
            if mda_id and state_id:
                from geoalchemy2.elements import WKTElement
                point = WKTElement(f"POINT({lng} {lat})", srid=4326)
                p = Project(
                    title=title, mda_id=mda_id, state_id=state_id,
                    contractor=contractor,
                    start_date=date.fromisoformat(start),
                    end_date=date.fromisoformat(end),
                    status=status,
                    budget_allocated=allocated,
                    spent=spent,
                    geolocation=point,
                    source="tracka",
                )
                session.add(p)
                pcount += 1
        session.flush()
        print(f"Seeded {pcount} projects with GPS coordinates")

        session.commit()
        print("All seed data committed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error seeding: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed OpenSpends database")
    parser.add_argument(
        "--db-url",
        default=os.environ.get(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/openspends"
        ),
    )
    args = parser.parse_args()

    seed(args.db_url)
