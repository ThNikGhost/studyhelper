"""Add work_id FK to files table.

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-03-02 12:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "l2m3n4o5p6q7"
down_revision = "k1l2m3n4o5p6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add work_id FK column and index to files table."""
    op.add_column(
        "files",
        sa.Column("work_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_files_work_id",
        "files",
        "works",
        ["work_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_files_work_id", "files", ["work_id"])


def downgrade() -> None:
    """Remove work_id index, FK, and column from files table."""
    op.drop_index("ix_files_work_id", table_name="files")
    op.drop_constraint("fk_files_work_id", "files", type_="foreignkey")
    op.drop_column("files", "work_id")
