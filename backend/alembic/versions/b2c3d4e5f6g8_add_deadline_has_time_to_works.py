"""add deadline_has_time to works

Revision ID: b2c3d4e5f6g8
Revises: a1b2c3d4e5f7
Create Date: 2026-02-19 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g8"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add deadline_has_time boolean to works table."""
    op.add_column(
        "works",
        sa.Column(
            "deadline_has_time",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.alter_column("works", "deadline_has_time", server_default=None)


def downgrade() -> None:
    """Remove deadline_has_time from works table."""
    op.drop_column("works", "deadline_has_time")
