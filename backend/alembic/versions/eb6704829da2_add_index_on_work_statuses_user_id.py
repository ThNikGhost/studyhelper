"""add index on work_statuses.user_id

Revision ID: eb6704829da2
Revises: c937e42e988d
Create Date: 2026-02-06 11:49:15.860712

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eb6704829da2"
down_revision: str | Sequence[str] | None = "c937e42e988d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add index on work_statuses.user_id for faster user-based queries."""
    op.create_index(
        op.f("ix_work_statuses_user_id"),
        "work_statuses",
        ["user_id"],
        unique=False,
        if_not_exists=True,
    )


def downgrade() -> None:
    """Remove index on work_statuses.user_id."""
    op.drop_index(
        op.f("ix_work_statuses_user_id"),
        table_name="work_statuses",
        if_exists=True,
    )
