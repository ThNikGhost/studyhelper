"""Add index on classmate_details.classmate_id.

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-02-21 00:00:00.000000
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "k1l2m3n4o5p6"
down_revision = "j0k1l2m3n4o5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add index on classmate_details.classmate_id for faster JOINs."""
    op.create_index(
        "ix_classmate_details_classmate_id",
        "classmate_details",
        ["classmate_id"],
    )


def downgrade() -> None:
    """Drop index on classmate_details.classmate_id."""
    op.drop_index("ix_classmate_details_classmate_id", table_name="classmate_details")
