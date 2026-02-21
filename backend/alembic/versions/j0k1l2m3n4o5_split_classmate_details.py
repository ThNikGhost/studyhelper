"""Split classmate details into per-user table.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-02-21

"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "j0k1l2m3n4o5"
down_revision = "i9j0k1l2m3n4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create classmate_details table and drop extended columns from classmates."""
    op.create_table(
        "classmate_details",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("classmate_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("short_name", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("telegram", sa.String(length=100), nullable=True),
        sa.Column("vk", sa.String(length=200), nullable=True),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["classmate_id"], ["classmates.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "classmate_id", "user_id", name="uq_classmate_details_classmate_user"
        ),
    )
    op.create_index("ix_classmate_details_user_id", "classmate_details", ["user_id"])

    # Drop extended columns from classmates table
    op.drop_column("classmates", "short_name")
    op.drop_column("classmates", "email")
    op.drop_column("classmates", "phone")
    op.drop_column("classmates", "telegram")
    op.drop_column("classmates", "vk")
    op.drop_column("classmates", "photo_url")
    op.drop_column("classmates", "notes")


def downgrade() -> None:
    """Drop classmate_details table and restore extended columns to classmates."""
    op.drop_index("ix_classmate_details_user_id", table_name="classmate_details")
    op.drop_table("classmate_details")

    op.add_column(
        "classmates", sa.Column("short_name", sa.String(length=100), nullable=True)
    )
    op.add_column(
        "classmates", sa.Column("email", sa.String(length=255), nullable=True)
    )
    op.add_column("classmates", sa.Column("phone", sa.String(length=50), nullable=True))
    op.add_column(
        "classmates", sa.Column("telegram", sa.String(length=100), nullable=True)
    )
    op.add_column("classmates", sa.Column("vk", sa.String(length=200), nullable=True))
    op.add_column(
        "classmates", sa.Column("photo_url", sa.String(length=500), nullable=True)
    )
    op.add_column("classmates", sa.Column("notes", sa.Text(), nullable=True))
