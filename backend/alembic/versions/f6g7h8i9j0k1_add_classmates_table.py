"""add classmates table

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-02-04 02:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f6g7h8i9j0k1"
down_revision: str | Sequence[str] | None = "e5f6g7h8i9j0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "classmates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("short_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("telegram", sa.String(100), nullable=True),
        sa.Column("vk", sa.String(200), nullable=True),
        sa.Column("photo_url", sa.String(500), nullable=True),
        sa.Column("group_name", sa.String(50), nullable=True),
        sa.Column("subgroup", sa.Integer(), nullable=True),
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
    )
    op.create_index("ix_classmates_full_name", "classmates", ["full_name"])
    op.create_index("ix_classmates_group_name", "classmates", ["group_name"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_classmates_group_name", table_name="classmates")
    op.drop_index("ix_classmates_full_name", table_name="classmates")
    op.drop_table("classmates")
