"""add_telegram_links_table

Revision ID: c7d8e9f0a1b2
Revises: 5a6b7c8d9e0f
Create Date: 2026-02-15 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7d8e9f0a1b2"
down_revision: str | None = "5a6b7c8d9e0f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create telegram_links table."""
    op.create_table(
        "telegram_links",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
        sa.Column("link_code", sa.String(length=6), nullable=True),
        sa.Column(
            "link_code_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "notify_deadlines", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column(
            "morning_summary", sa.Boolean(), nullable=False, server_default="true"
        ),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=True),
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
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_telegram_links_user_id", "telegram_links", ["user_id"], unique=True
    )
    op.create_index(
        "ix_telegram_links_telegram_id", "telegram_links", ["telegram_id"], unique=True
    )
    op.create_index("ix_telegram_links_link_code", "telegram_links", ["link_code"])


def downgrade() -> None:
    """Drop telegram_links table."""
    op.drop_index("ix_telegram_links_link_code", table_name="telegram_links")
    op.drop_index("ix_telegram_links_telegram_id", table_name="telegram_links")
    op.drop_index("ix_telegram_links_user_id", table_name="telegram_links")
    op.drop_table("telegram_links")
