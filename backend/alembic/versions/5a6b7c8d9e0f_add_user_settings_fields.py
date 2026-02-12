"""add_user_settings_fields

Revision ID: 5a6b7c8d9e0f
Revises: 488c2925b15c
Create Date: 2026-02-12 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a6b7c8d9e0f"
down_revision: str | None = "488c2925b15c"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Add user settings fields for cross-device sync."""
    op.add_column("users", sa.Column("preferred_subgroup", sa.Integer(), nullable=True))
    op.add_column(
        "users", sa.Column("preferred_pe_teacher", sa.String(200), nullable=True)
    )
    op.add_column("users", sa.Column("theme_mode", sa.String(10), nullable=True))


def downgrade() -> None:
    """Remove user settings fields."""
    op.drop_column("users", "theme_mode")
    op.drop_column("users", "preferred_pe_teacher")
    op.drop_column("users", "preferred_subgroup")
