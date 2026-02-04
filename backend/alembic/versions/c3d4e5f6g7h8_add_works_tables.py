"""add works tables

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2026-02-04 00:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6g7h8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6g7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Works table
    op.create_table(
        "works",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("work_type", sa.String(20), nullable=False),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_grade", sa.Integer(), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=False),
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
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_works_subject_id", "works", ["subject_id"])
    op.create_index("ix_works_deadline", "works", ["deadline"])

    # Work statuses table
    op.create_table(
        "work_statuses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="not_started"
        ),
        sa.Column("grade", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
            ["work_id"],
            ["works.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index("ix_work_statuses_work_id", "work_statuses", ["work_id"])
    op.create_index("ix_work_statuses_user_id", "work_statuses", ["user_id"])
    op.create_index(
        "ix_work_statuses_work_user",
        "work_statuses",
        ["work_id", "user_id"],
        unique=True,
    )

    # Work status history table
    op.create_table(
        "work_status_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_status_id", sa.Integer(), nullable=False),
        sa.Column("old_status", sa.String(20), nullable=True),
        sa.Column("new_status", sa.String(20), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("changed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["work_status_id"],
            ["work_statuses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
    )
    op.create_index(
        "ix_work_status_history_work_status_id",
        "work_status_history",
        ["work_status_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_work_status_history_work_status_id", table_name="work_status_history"
    )
    op.drop_table("work_status_history")

    op.drop_index("ix_work_statuses_work_user", table_name="work_statuses")
    op.drop_index("ix_work_statuses_user_id", table_name="work_statuses")
    op.drop_index("ix_work_statuses_work_id", table_name="work_statuses")
    op.drop_table("work_statuses")

    op.drop_index("ix_works_deadline", table_name="works")
    op.drop_index("ix_works_subject_id", table_name="works")
    op.drop_table("works")
