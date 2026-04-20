"""Modelo de eventos processados para idempotencia de webhook."""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ProcessedWebhookEvent(Base):
    """Representa evento identificado por `event_id` ou `message_id` ja processado."""

    __tablename__ = "processed_webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str | None] = mapped_column(String(191), nullable=True)
    message_id: Mapped[str | None] = mapped_column(String(191), nullable=True)
    session_id: Mapped[str] = mapped_column(String(120), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
