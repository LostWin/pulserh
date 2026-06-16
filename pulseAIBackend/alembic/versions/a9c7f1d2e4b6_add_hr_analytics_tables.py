"""add hr analytics tables

Revision ID: a9c7f1d2e4b6
Revises: e1a4c9d52b31
Create Date: 2026-06-15 15:15:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a9c7f1d2e4b6"
down_revision: Union[str, Sequence[str], None] = "e1a4c9d52b31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skills",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_skills_name"), "skills", ["name"], unique=True)

    op.create_table(
        "employee_skills",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("proficiency_level", sa.String(), nullable=False, server_default="intermediate"),
        sa.Column("years_experience", sa.Float(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_employee_skills_employee_id"), "employee_skills", ["employee_id"], unique=False)
    op.create_index(op.f("ix_employee_skills_skill_id"), "employee_skills", ["skill_id"], unique=False)

    op.create_table(
        "training_courses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("duration_hours", sa.Float(), nullable=True),
        sa.Column("level", sa.String(), nullable=True),
        sa.Column("format", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_skill_id", sa.String(), nullable=True),
        sa.Column("required_for_job_family", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(["target_skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "training_enrollments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("training_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="assigned"),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("mandatory", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["training_id"], ["training_courses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_training_enrollments_employee_id"), "training_enrollments", ["employee_id"], unique=False)
    op.create_index(op.f("ix_training_enrollments_training_id"), "training_enrollments", ["training_id"], unique=False)

    op.create_table(
        "project_assignments",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("role_on_project", sa.String(), nullable=True),
        sa.Column("allocation_pct", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_assignments_employee_id"), "project_assignments", ["employee_id"], unique=False)
    op.create_index(op.f("ix_project_assignments_project_id"), "project_assignments", ["project_id"], unique=False)

    op.create_table(
        "engagement_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(), nullable=False, server_default="survey"),
        sa.Column("pulse_label", sa.String(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_engagement_snapshots_employee_id"), "engagement_snapshots", ["employee_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_engagement_snapshots_employee_id"), table_name="engagement_snapshots")
    op.drop_table("engagement_snapshots")
    op.drop_index(op.f("ix_project_assignments_project_id"), table_name="project_assignments")
    op.drop_index(op.f("ix_project_assignments_employee_id"), table_name="project_assignments")
    op.drop_table("project_assignments")
    op.drop_index(op.f("ix_training_enrollments_training_id"), table_name="training_enrollments")
    op.drop_index(op.f("ix_training_enrollments_employee_id"), table_name="training_enrollments")
    op.drop_table("training_enrollments")
    op.drop_table("training_courses")
    op.drop_index(op.f("ix_employee_skills_skill_id"), table_name="employee_skills")
    op.drop_index(op.f("ix_employee_skills_employee_id"), table_name="employee_skills")
    op.drop_table("employee_skills")
    op.drop_index(op.f("ix_skills_name"), table_name="skills")
    op.drop_table("skills")
