"""add status to leads

Revision ID: 20260420_0003
Revises: 20260420_0002
Create Date: 2026-04-20 00:30:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260420_0003"
down_revision: str | Sequence[str] | None = "20260420_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona coluna de status operacional no lead."""
    op.add_column("leads", sa.Column("status", sa.String(length=40), nullable=True))
    op.create_index("ix_leads_status", "leads", ["status"], unique=False)


def downgrade() -> None:
    """Remove coluna de status operacional do lead."""
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_column("leads", "status")
