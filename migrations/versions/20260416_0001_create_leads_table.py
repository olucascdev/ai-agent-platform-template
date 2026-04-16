"""create leads table

Revision ID: 20260416_0001
Revises:
Create Date: 2026-04-16 00:00:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260416_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabela principal de leads para correlacao de sessao e CRM."""
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("session_id", sa.String(length=120), nullable=False),
        sa.Column("crm_contact_id", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone", name="uq_leads_phone"),
    )
    op.create_index("ix_leads_session_id", "leads", ["session_id"], unique=False)


def downgrade() -> None:
    """Remove estrutura inicial de leads."""
    op.drop_index("ix_leads_session_id", table_name="leads")
    op.drop_table("leads")
