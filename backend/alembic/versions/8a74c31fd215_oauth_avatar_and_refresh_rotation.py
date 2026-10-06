"""Add OAuth profile metadata and safe refresh rotation state.

Revision ID: 8a74c31fd215
Revises: 185bfcd38538
Create Date: 2026-10-05
"""
from alembic import op
import sqlalchemy as sa


revision = "8a74c31fd215"
down_revision = "185bfcd38538"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("avatar_url", sa.String(length=2048), nullable=True))
    op.add_column("refresh_tokens", sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("refresh_tokens", sa.Column("rotation_successor_id", sa.String(length=36), nullable=True))


def downgrade() -> None:
    op.drop_column("refresh_tokens", "rotation_successor_id")
    op.drop_column("refresh_tokens", "rotated_at")
    op.drop_column("users", "avatar_url")
