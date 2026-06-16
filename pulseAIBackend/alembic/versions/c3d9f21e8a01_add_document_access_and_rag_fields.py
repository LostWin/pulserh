"""Add document access and rag fields

Revision ID: c3d9f21e8a01
Revises: b7d9a3f4c2aa
Create Date: 2026-06-14 15:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d9f21e8a01'
down_revision: Union[str, Sequence[str], None] = 'b7d9a3f4c2aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("allowed_roles", sa.JSON(), nullable=True))
    op.add_column("documents", sa.Column("rag_enabled", sa.Boolean(), nullable=True))
    op.add_column("documents", sa.Column("rag_status", sa.String(), nullable=True))
    op.add_column("documents", sa.Column("rag_last_synced_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("rag_error", sa.Text(), nullable=True))

    op.execute("""UPDATE documents SET allowed_roles = '["hr","admin"]'::json WHERE allowed_roles IS NULL""")
    op.execute("""UPDATE documents SET rag_enabled = false WHERE rag_enabled IS NULL""")
    op.execute("""UPDATE documents SET rag_status = 'disabled' WHERE rag_status IS NULL""")

    op.alter_column("documents", "allowed_roles", existing_type=sa.JSON(), nullable=False)
    op.alter_column("documents", "rag_enabled", existing_type=sa.Boolean(), nullable=False)
    op.alter_column("documents", "rag_status", existing_type=sa.String(), nullable=False)

    op.create_table(
        "document_access_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("user_email", sa.String(), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("roles", sa.JSON(), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_access_events_document_id"), "document_access_events", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_document_access_events_document_id"), table_name="document_access_events")
    op.drop_table("document_access_events")
    op.drop_column("documents", "rag_error")
    op.drop_column("documents", "rag_last_synced_at")
    op.drop_column("documents", "rag_status")
    op.drop_column("documents", "rag_enabled")
    op.drop_column("documents", "allowed_roles")
