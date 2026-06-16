"""Fix import history created_at default

Revision ID: b7d9a3f4c2aa
Revises: 6d5ee9b9d3e1
Create Date: 2026-06-14 14:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7d9a3f4c2aa'
down_revision: Union[str, Sequence[str], None] = '6d5ee9b9d3e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE import_history SET created_at = NOW() WHERE created_at IS NULL")
    op.alter_column(
        "import_history",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.text("NOW()"),
    )


def downgrade() -> None:
    op.alter_column(
        "import_history",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        nullable=True,
        server_default=None,
    )
