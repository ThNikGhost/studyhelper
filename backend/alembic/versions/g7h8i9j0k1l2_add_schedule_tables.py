"""add schedule tables

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-02-04 02:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "g7h8i9j0k1l2"
down_revision: str | Sequence[str] | None = "f6g7h8i9j0k1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Schedule entries table
    op.create_table(
        "schedule_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("week_type", sa.String(20), nullable=True),
        sa.Column("subject_name", sa.String(200), nullable=False),
        sa.Column("lesson_type", sa.String(20), nullable=False),
        sa.Column("teacher_name", sa.String(200), nullable=True),
        sa.Column("room", sa.String(50), nullable=True),
        sa.Column("building", sa.String(100), nullable=True),
        sa.Column("group_name", sa.String(50), nullable=True),
        sa.Column("subgroup", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("teacher_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["teachers.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_schedule_entries_day_of_week", "schedule_entries", ["day_of_week"]
    )
    op.create_index("ix_schedule_entries_week_type", "schedule_entries", ["week_type"])

    # Schedule snapshots table
    op.create_table(
        "schedule_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("raw_data", sa.Text(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("entries_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_schedule_snapshots_date", "schedule_snapshots", ["snapshot_date"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_schedule_snapshots_date", table_name="schedule_snapshots")
    op.drop_table("schedule_snapshots")

    op.drop_index("ix_schedule_entries_week_type", table_name="schedule_entries")
    op.drop_index("ix_schedule_entries_day_of_week", table_name="schedule_entries")
    op.drop_table("schedule_entries")
