"""add benefits and career models

Revision ID: f6a9b3d4c1e2
Revises: e4b2c7d9a1f0
Create Date: 2026-06-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6a9b3d4c1e2"
down_revision = "e4b2c7d9a1f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "benefit_plans",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("coverage_summary", sa.Text(), nullable=True),
        sa.Column("enrollment_month", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "employee_benefits",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("benefit_plan_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("renewal_date", sa.Date(), nullable=True),
        sa.Column("tier_label", sa.String(), nullable=True),
        sa.Column("employer_contribution", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["benefit_plan_id"], ["benefit_plans.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_benefits_benefit_plan_id"), "employee_benefits", ["benefit_plan_id"], unique=False)
    op.create_index(op.f("ix_employee_benefits_employee_id"), "employee_benefits", ["employee_id"], unique=False)

    op.create_table(
        "career_paths",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("target_job_id", sa.String(), nullable=True),
        sa.Column("target_title", sa.String(), nullable=False),
        sa.Column("readiness_level", sa.String(), nullable=False),
        sa.Column("next_step", sa.Text(), nullable=True),
        sa.Column("mentor_name", sa.String(), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["target_job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_career_paths_employee_id"), "career_paths", ["employee_id"], unique=False)
    op.create_index(op.f("ix_career_paths_target_job_id"), "career_paths", ["target_job_id"], unique=False)

    op.create_table(
        "mobility_requests",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("target_department_id", sa.String(), nullable=True),
        sa.Column("target_job_id", sa.String(), nullable=True),
        sa.Column("request_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["target_department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["target_job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mobility_requests_employee_id"), "mobility_requests", ["employee_id"], unique=False)
    op.create_index(op.f("ix_mobility_requests_target_department_id"), "mobility_requests", ["target_department_id"], unique=False)
    op.create_index(op.f("ix_mobility_requests_target_job_id"), "mobility_requests", ["target_job_id"], unique=False)

    op.create_table(
        "promotion_history",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("previous_job_title", sa.String(), nullable=True),
        sa.Column("new_job_title", sa.String(), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_promotion_history_employee_id"), "promotion_history", ["employee_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_promotion_history_employee_id"), table_name="promotion_history")
    op.drop_table("promotion_history")
    op.drop_index(op.f("ix_mobility_requests_target_job_id"), table_name="mobility_requests")
    op.drop_index(op.f("ix_mobility_requests_target_department_id"), table_name="mobility_requests")
    op.drop_index(op.f("ix_mobility_requests_employee_id"), table_name="mobility_requests")
    op.drop_table("mobility_requests")
    op.drop_index(op.f("ix_career_paths_target_job_id"), table_name="career_paths")
    op.drop_index(op.f("ix_career_paths_employee_id"), table_name="career_paths")
    op.drop_table("career_paths")
    op.drop_index(op.f("ix_employee_benefits_employee_id"), table_name="employee_benefits")
    op.drop_index(op.f("ix_employee_benefits_benefit_plan_id"), table_name="employee_benefits")
    op.drop_table("employee_benefits")
    op.drop_table("benefit_plans")
