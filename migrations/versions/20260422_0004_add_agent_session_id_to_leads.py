"""add agent_session_id to leads

Revision ID: 20260422_0004
Revises: 20260420_0003
Create Date: 2026-04-22 00:40:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260422_0004"
down_revision: str | Sequence[str] | None = "20260420_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Adiciona sessao interna do agente sem perder dados existentes."""
    op.add_column("leads", sa.Column("agent_session_id", sa.String(length=120), nullable=True))
    op.execute('UPDATE "leads" SET "agent_session_id" = "session_id" WHERE "agent_session_id" IS NULL')
    op.alter_column("leads", "agent_session_id", nullable=False)
    op.create_index("ix_leads_agent_session_id", "leads", ["agent_session_id"], unique=False)


def downgrade() -> None:
    """Remove coluna de sessao interna do agente."""
    op.drop_index("ix_leads_agent_session_id", table_name="leads")
    op.drop_column("leads", "agent_session_id")
