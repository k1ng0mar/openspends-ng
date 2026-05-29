"""Initial migration — create all tables."""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # States
    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("capital", sa.String(100)),
        sa.Column("region", sa.String(50)),
    )

    # LGAs
    op.create_table(
        "lgas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("state_id", sa.Integer(), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20)),
        sa.UniqueConstraint("state_id", "name"),
    )

    # MDAs
    op.create_table(
        "mdas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), unique=True),
        sa.Column("level", sa.String(10), nullable=False),
        sa.Column("state_id", sa.Integer(), sa.ForeignKey("states.id")),
        sa.Column("lga_id", sa.Integer(), sa.ForeignKey("lgas.id")),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("mdas.id")),
        sa.Column("ncoa_sector", sa.String(10)),
        sa.Index("idx_mda_level", "level"),
        sa.Index("idx_mda_state", "state_id"),
    )

    # Fiscal Years
    op.create_table(
        "fiscal_years",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("year", sa.Integer(), nullable=False, unique=True),
        sa.Column("is_current", sa.Boolean(), default=False),
    )

    # NCOA
    op.create_table(
        "ncoa",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("description", sa.String(300)),
        sa.Column("category", sa.String(100)),
        sa.Column("chapter", sa.String(100)),
        sa.Column("group_name", sa.String(100)),
    )

    # Budgets
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mda_id", sa.Integer(), sa.ForeignKey("mdas.id"), nullable=False),
        sa.Column("year_id", sa.Integer(), sa.ForeignKey("fiscal_years.id"), nullable=False),
        sa.Column("season", sa.String(10), nullable=False),
        sa.Column("approved", sa.Float()),
        sa.Column("revised", sa.Float()),
        sa.Column("estimated", sa.Float()),
        sa.Column("spent", sa.Float()),
        sa.Column("variance_pct", sa.Float()),
        sa.Column("source_url", sa.String(500)),
        sa.Column("updated_at", sa.DateTime()),
        sa.Index("idx_budget_mda_year", "mda_id", "year_id"),
        sa.UniqueConstraint("mda_id", "year_id", "season"),
    )

    # Spending
    op.create_table(
        "spending",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mda_id", sa.Integer(), sa.ForeignKey("mdas.id"), nullable=False),
        sa.Column("beneficiary", sa.String(300)),
        sa.Column("purpose", sa.Text()),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("reference", sa.String(100)),
        sa.Column("location_id", sa.String(50)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("source", sa.String(50)),
        sa.Column("created_at", sa.DateTime()),
        sa.Index("idx_spending_date_mda", "date", "mda_id"),
        sa.Index("idx_spending_amount", "amount"),
    )

    # Projects (with PostGIS)
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("mda_id", sa.Integer(), sa.ForeignKey("mdas.id")),
        sa.Column("state_id", sa.Integer(), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("lga_id", sa.Integer(), sa.ForeignKey("lgas.id")),
        sa.Column("budget_id", sa.Integer(), sa.ForeignKey("budgets.id")),
        sa.Column("contractor", sa.String(300)),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("status", sa.String(20), default="not_started"),
        sa.Column("budget_allocated", sa.Float()),
        sa.Column("spent", sa.Float(), default=0),
        sa.Column("geolocation", Geometry("POINT", srid=4326)),
        sa.Column("photos", sa.Text()),
        sa.Column("source", sa.String(50)),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.Index("idx_project_state_status", "state_id", "status"),
        sa.Index("idx_project_mda", "mda_id"),
    )

    # Geolocation Cache
    op.create_table(
        "geolocation_cache",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("address", sa.String(300)),
        sa.Column("state", sa.String(100)),
        sa.Column("lga", sa.String(100)),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("source", sa.String(50)),
        sa.Column("created_at", sa.DateTime()),
    )

    # Contracts (OCDS)
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ocid", sa.String(100), unique=True),
        sa.Column("title", sa.String(500)),
        sa.Column("mda_id", sa.Integer(), sa.ForeignKey("mdas.id")),
        sa.Column("amount", sa.Float()),
        sa.Column("status", sa.String(50)),
        sa.Column("award_date", sa.Date()),
        sa.Column("supplier", sa.String(300)),
        sa.Column("source_data", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
        sa.Index("idx_contract_ocid", "ocid"),
    )


def downgrade() -> None:
    op.drop_table("contracts")
    op.drop_table("geolocation_cache")
    op.drop_table("projects")
    op.drop_table("spending")
    op.drop_table("budgets")
    op.drop_table("ncoa")
    op.drop_table("fiscal_years")
    op.drop_table("mdas")
    op.drop_table("lgas")
    op.drop_table("states")
