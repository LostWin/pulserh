"""add data access policies

Revision ID: e1a4c9d52b31
Revises: d4c8a7e91b2f
Create Date: 2026-06-15 12:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1a4c9d52b31"
down_revision: Union[str, Sequence[str], None] = "d4c8a7e91b2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_access_policies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("resource", sa.String(), nullable=False),
        sa.Column("scope", sa.String(), nullable=False),
        sa.Column("field_key", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("visibility", sa.String(), nullable=False, server_default="visible"),
        sa.Column("mask_type", sa.String(), nullable=True),
        sa.Column("conditions_json", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource", "scope", "field_key", "role", name="uq_data_access_policy_scope_field_role"),
    )
    op.create_index(op.f("ix_data_access_policies_resource"), "data_access_policies", ["resource"], unique=False)
    op.create_index(op.f("ix_data_access_policies_scope"), "data_access_policies", ["scope"], unique=False)
    op.create_index(op.f("ix_data_access_policies_field_key"), "data_access_policies", ["field_key"], unique=False)
    op.create_index(op.f("ix_data_access_policies_role"), "data_access_policies", ["role"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_data_access_policies_role"), table_name="data_access_policies")
    op.drop_index(op.f("ix_data_access_policies_field_key"), table_name="data_access_policies")
    op.drop_index(op.f("ix_data_access_policies_scope"), table_name="data_access_policies")
    op.drop_index(op.f("ix_data_access_policies_resource"), table_name="data_access_policies")
    op.drop_table("data_access_policies")
