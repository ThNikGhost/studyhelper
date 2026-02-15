"""add widget_api_keys table

Revision ID: 02665a1d4d94
Revises: d01120901766
Create Date: 2026-02-15 23:10:15.974570

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "02665a1d4d94"
down_revision: str | Sequence[str] | None = "d01120901766"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "widget_api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_widget_api_keys_token"), "widget_api_keys", ["token"], unique=True
    )
    op.create_index(
        op.f("ix_widget_api_keys_user_id"), "widget_api_keys", ["user_id"], unique=True
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_widget_api_keys_user_id"), table_name="widget_api_keys")
    op.drop_index(op.f("ix_widget_api_keys_token"), table_name="widget_api_keys")
    op.drop_table("widget_api_keys")
