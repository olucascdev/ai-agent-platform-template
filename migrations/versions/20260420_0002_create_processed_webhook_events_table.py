"""create processed webhook events table

Revision ID: 20260420_0002
Revises: 20260416_0001
Create Date: 2026-04-20 00:00:00.000000

"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260420_0002"
down_revision: str | Sequence[str] | None = "20260416_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabela de idempotencia para eventos de webhook processados."""
    op.create_table(
        "processed_webhook_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=191), nullable=True),
        sa.Column("message_id", sa.String(length=191), nullable=True),
        sa.Column("session_id", sa.String(length=120), nullable=False),
        sa.Column("contact_phone", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "event_id IS NOT NULL OR message_id IS NOT NULL",
            name="ck_processed_webhook_events_has_identifier",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_processed_webhook_events_event_id",
        "processed_webhook_events",
        ["event_id"],
        unique=True,
    )
    op.create_index(
        "uq_processed_webhook_events_message_id",
        "processed_webhook_events",
        ["message_id"],
        unique=True,
    )


def downgrade() -> None:
    """Remove tabela de idempotencia de webhook."""
    op.drop_index("uq_processed_webhook_events_message_id", table_name="processed_webhook_events")
    op.drop_index("uq_processed_webhook_events_event_id", table_name="processed_webhook_events")
    op.drop_table("processed_webhook_events")
