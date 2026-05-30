"""Add pipeline infrastructure tables: pipeline_runs, data_sources, and dedup columns.

Revision ID: 0002_pipeline_infrastructure
Revises: 0001_init
Create Date: 2026-05-29
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0002_pipeline_infrastructure"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Pipeline Run Tracking ──
    op.create_table(
        "pipeline_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("records_found", sa.Integer(), server_default="0"),
        sa.Column("records_inserted", sa.Integer(), server_default="0"),
        sa.Column("records_updated", sa.Integer(), server_default="0"),
        sa.Column("records_skipped", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("details", sa.JSON()),
        sa.Index("idx_pipeline_source_status", "source", "status"),
        sa.Index("idx_pipeline_started", "started_at"),
    )

    # ── Data Source Registry ──
    op.create_table(
        "data_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200)),
        sa.Column("base_url", sa.String(500)),
        sa.Column("source_type", sa.String(20)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true_()),
        sa.Column("schedule", sa.String(100)),
        sa.Column("last_success_at", sa.DateTime()),
        sa.Column("last_run_at", sa.DateTime()),
        sa.Column("run_count", sa.Integer(), server_default="0"),
        sa.Column("fail_count", sa.Integer(), server_default="0"),
        sa.Column("config", sa.JSON()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Dedup hash columns on existing tables ──
    op.add_column(
        "spending",
        sa.Column("source_hash", sa.String(64), nullable=True),
    )
    op.create_index("idx_spending_source_hash", "spending", ["source_hash"])

    op.add_column(
        "projects",
        sa.Column("source_hash", sa.String(64), nullable=True),
    )
    op.create_index("idx_project_source_hash", "projects", ["source_hash"])


def downgrade() -> None:
    op.drop_index("idx_project_source_hash", table_name="projects")
    op.drop_column("projects", "source_hash")

    op.drop_index("idx_spending_source_hash", table_name="spending")
    op.drop_column("spending", "source_hash")

    op.drop_table("data_sources")
    op.drop_table("pipeline_runs")
