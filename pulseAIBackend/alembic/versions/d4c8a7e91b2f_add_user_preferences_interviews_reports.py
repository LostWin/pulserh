"""add user preferences interviews reports

Revision ID: d4c8a7e91b2f
Revises: c3d9f21e8a01
Create Date: 2026-06-15 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4c8a7e91b2f"
down_revision: Union[str, Sequence[str], None] = "c3d9f21e8a01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("avatar_data_url", sa.Text(), nullable=True),
        sa.Column("theme", sa.String(), nullable=False, server_default="dark"),
        sa.Column("locale", sa.String(), nullable=False, server_default="fr"),
        sa.Column("timezone", sa.String(), nullable=False, server_default="Africa/Lome"),
        sa.Column("digest_frequency", sa.String(), nullable=False, server_default="daily"),
        sa.Column("profile_title", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_preferences_user_id"), "user_preferences", ["user_id"], unique=True)

    op.create_table(
        "interviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("employee_id", sa.String(), nullable=False),
        sa.Column("manager_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False, server_default="Entretien individuel"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="Planifié"),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["manager_id"], ["employees.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interviews_employee_id"), "interviews", ["employee_id"], unique=False)
    op.create_index(op.f("ix_interviews_manager_id"), "interviews", ["manager_id"], unique=False)

    op.create_table(
        "generated_reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("period", sa.String(), nullable=False),
        sa.Column("department_filter", sa.String(), nullable=True),
        sa.Column("format", sa.String(), nullable=False, server_default="PDF"),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="ready"),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("generated_reports")
    op.drop_index(op.f("ix_interviews_manager_id"), table_name="interviews")
    op.drop_index(op.f("ix_interviews_employee_id"), table_name="interviews")
    op.drop_table("interviews")
    op.drop_index(op.f("ix_user_preferences_user_id"), table_name="user_preferences")
    op.drop_table("user_preferences")
