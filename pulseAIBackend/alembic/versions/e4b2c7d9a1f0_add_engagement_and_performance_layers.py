"""add engagement and performance layers

Revision ID: e4b2c7d9a1f0
Revises: d2f4c6b8e1aa
Create Date: 2026-06-15 22:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e4b2c7d9a1f0"
down_revision = "d2f4c6b8e1aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("engagement_snapshots", sa.Column("trend", sa.Integer(), nullable=True))
    op.add_column("engagement_snapshots", sa.Column("risk_band", sa.String(), nullable=True))
    op.add_column("engagement_snapshots", sa.Column("source_signals", sa.JSON(), nullable=True))

    op.create_table(
        "engagement_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("intensity", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_engagement_events_employee_id"), "engagement_events", ["employee_id"], unique=False)

    op.add_column("interviews", sa.Column("interview_type", sa.String(), nullable=True))
    op.add_column("interviews", sa.Column("duration_minutes", sa.Integer(), nullable=True))
    op.add_column("interviews", sa.Column("outcome", sa.String(), nullable=True))
    op.add_column("interviews", sa.Column("summary", sa.Text(), nullable=True))
    op.add_column("interviews", sa.Column("next_actions", sa.JSON(), nullable=True))
    op.execute("UPDATE interviews SET interview_type = 'one_on_one' WHERE interview_type IS NULL")
    op.alter_column("interviews", "interview_type", nullable=False, existing_type=sa.String())

    op.create_table(
        "performance_reviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("reviewer_id", sa.String(), nullable=True),
        sa.Column("review_type", sa.String(), nullable=False),
        sa.Column("period_label", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("improvement_areas", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["reviewer_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_reviews_employee_id"), "performance_reviews", ["employee_id"], unique=False)
    op.create_index(op.f("ix_performance_reviews_reviewer_id"), "performance_reviews", ["reviewer_id"], unique=False)

    op.create_table(
        "performance_objectives",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("progress_pct", sa.Integer(), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["owner_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_performance_objectives_employee_id"), "performance_objectives", ["employee_id"], unique=False)
    op.create_index(op.f("ix_performance_objectives_owner_id"), "performance_objectives", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_performance_objectives_owner_id"), table_name="performance_objectives")
    op.drop_index(op.f("ix_performance_objectives_employee_id"), table_name="performance_objectives")
    op.drop_table("performance_objectives")

    op.drop_index(op.f("ix_performance_reviews_reviewer_id"), table_name="performance_reviews")
    op.drop_index(op.f("ix_performance_reviews_employee_id"), table_name="performance_reviews")
    op.drop_table("performance_reviews")

    op.drop_column("interviews", "next_actions")
    op.drop_column("interviews", "summary")
    op.drop_column("interviews", "outcome")
    op.drop_column("interviews", "duration_minutes")
    op.drop_column("interviews", "interview_type")

    op.drop_index(op.f("ix_engagement_events_employee_id"), table_name="engagement_events")
    op.drop_table("engagement_events")

    op.drop_column("engagement_snapshots", "source_signals")
    op.drop_column("engagement_snapshots", "risk_band")
    op.drop_column("engagement_snapshots", "trend")
