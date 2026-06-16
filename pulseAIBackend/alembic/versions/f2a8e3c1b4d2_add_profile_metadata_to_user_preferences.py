"""add profile metadata to user preferences

Revision ID: f2a8e3c1b4d2
Revises: e1a4c9d52b31
Create Date: 2026-06-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f2a8e3c1b4d2"
down_revision = "e1a4c9d52b31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user_preferences", sa.Column("birth_date_label", sa.String(), nullable=True))
    op.add_column("user_preferences", sa.Column("address_label", sa.Text(), nullable=True))
    op.add_column("user_preferences", sa.Column("work_location_label", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("user_preferences", "work_location_label")
    op.drop_column("user_preferences", "address_label")
    op.drop_column("user_preferences", "birth_date_label")
