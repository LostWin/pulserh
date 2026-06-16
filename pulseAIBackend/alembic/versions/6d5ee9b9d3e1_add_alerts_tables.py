"""add alerts tables

Revision ID: 6d5ee9b9d3e1
Revises: b165226068f0
Create Date: 2026-06-14 14:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d5ee9b9d3e1"
down_revision: Union[str, Sequence[str], None] = "b165226068f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=True),
        sa.Column("workflow_id", sa.String(), nullable=True),
        sa.Column("target_user_id", sa.String(), nullable=True),
        sa.Column("target_roles", sa.JSON(), nullable=True),
        sa.Column("link", sa.String(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("action_plan", sa.Text(), nullable=True),
        sa.Column("resolved_by", sa.String(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["workflow_id"], ["workflows.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alerts_employee_id"), "alerts", ["employee_id"], unique=False)
    op.create_index(op.f("ix_alerts_fingerprint"), "alerts", ["fingerprint"], unique=True)
    op.create_index(op.f("ix_alerts_target_user_id"), "alerts", ["target_user_id"], unique=False)
    op.create_index(op.f("ix_alerts_workflow_id"), "alerts", ["workflow_id"], unique=False)

    op.create_table(
        "alert_recipient_states",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("alert_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_recipient_states_alert_id"), "alert_recipient_states", ["alert_id"], unique=False)
    op.create_index(op.f("ix_alert_recipient_states_user_id"), "alert_recipient_states", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_alert_recipient_states_user_id"), table_name="alert_recipient_states")
    op.drop_index(op.f("ix_alert_recipient_states_alert_id"), table_name="alert_recipient_states")
    op.drop_table("alert_recipient_states")
    op.drop_index(op.f("ix_alerts_workflow_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_target_user_id"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_fingerprint"), table_name="alerts")
    op.drop_index(op.f("ix_alerts_employee_id"), table_name="alerts")
    op.drop_table("alerts")
