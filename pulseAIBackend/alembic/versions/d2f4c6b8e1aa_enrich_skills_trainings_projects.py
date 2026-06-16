"""enrich skills trainings projects

Revision ID: d2f4c6b8e1aa
Revises: c8b1d7e4f9aa
Create Date: 2026-06-15 21:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d2f4c6b8e1aa"
down_revision = "c8b1d7e4f9aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("priority", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("business_domain", sa.String(), nullable=True))
    op.add_column("projects", sa.Column("required_skill_ids", sa.JSON(), nullable=True))
    op.add_column("projects", sa.Column("manager_id", sa.String(), nullable=True))
    op.create_foreign_key("fk_projects_manager", "projects", "employees", ["manager_id"], ["id"])

    op.add_column("skills", sa.Column("level_scale", sa.String(), nullable=True))
    op.add_column("skills", sa.Column("is_certifiable", sa.Boolean(), nullable=True))
    op.add_column("skills", sa.Column("is_active", sa.Boolean(), nullable=True))

    op.add_column("employee_skills", sa.Column("source", sa.String(), nullable=True))
    op.add_column("employee_skills", sa.Column("validated_by", sa.String(), nullable=True))
    op.add_column("employee_skills", sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("employee_skills", sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("employee_skills", sa.Column("confidence_score", sa.Float(), nullable=True))

    op.add_column("training_courses", sa.Column("difficulty", sa.String(), nullable=True))
    op.add_column("training_courses", sa.Column("delivery_mode", sa.String(), nullable=True))
    op.add_column("training_courses", sa.Column("mandatory_for_roles", sa.JSON(), nullable=True))

    op.add_column("training_enrollments", sa.Column("assigned_by", sa.String(), nullable=True))
    op.add_column("training_enrollments", sa.Column("recommendation_reason", sa.Text(), nullable=True))

    op.execute("UPDATE skills SET is_certifiable = false WHERE is_certifiable IS NULL")
    op.execute("UPDATE skills SET is_active = true WHERE is_active IS NULL")
    op.alter_column("skills", "is_certifiable", nullable=False, existing_type=sa.Boolean())
    op.alter_column("skills", "is_active", nullable=False, existing_type=sa.Boolean())


def downgrade() -> None:
    op.drop_column("training_enrollments", "recommendation_reason")
    op.drop_column("training_enrollments", "assigned_by")

    op.drop_column("training_courses", "mandatory_for_roles")
    op.drop_column("training_courses", "delivery_mode")
    op.drop_column("training_courses", "difficulty")

    op.drop_column("employee_skills", "confidence_score")
    op.drop_column("employee_skills", "last_used_at")
    op.drop_column("employee_skills", "validated_at")
    op.drop_column("employee_skills", "validated_by")
    op.drop_column("employee_skills", "source")

    op.drop_column("skills", "is_active")
    op.drop_column("skills", "is_certifiable")
    op.drop_column("skills", "level_scale")

    op.drop_constraint("fk_projects_manager", "projects", type_="foreignkey")
    op.drop_column("projects", "manager_id")
    op.drop_column("projects", "required_skill_ids")
    op.drop_column("projects", "business_domain")
    op.drop_column("projects", "priority")
