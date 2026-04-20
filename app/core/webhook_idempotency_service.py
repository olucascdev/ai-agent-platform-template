"""Servico de idempotencia para eventos de webhook por event/message id."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.models import ProcessedWebhookEvent
from db.session import AsyncSessionLocal

SessionFactory = Callable[[], Any]


@dataclass(frozen=True, slots=True)
class IdempotencyDecision:
    """Resultado de verificacao idempotente de um evento de webhook."""

    is_duplicate: bool
    idempotency_key: str | None


class WebhookIdempotencyService:
    """Registra eventos processados e detecta duplicidade por IDs estaveis."""

    def __init__(self, session_factory: SessionFactory = AsyncSessionLocal) -> None:
        self._session_factory = session_factory

    async def register_or_detect_duplicate(
        self,
        *,
        event_id: str | None,
        message_id: str | None,
        session_id: str,
        contact_phone: str,
    ) -> IdempotencyDecision:
        """Registra evento quando inedito ou marca como duplicado quando ja processado."""
        normalized_event_id = _normalize_optional(event_id)
        normalized_message_id = _normalize_optional(message_id)
        normalized_session_id = _normalize_required(session_id, field_name="session_id")
        normalized_contact_phone = _normalize_required(contact_phone, field_name="contact_phone")

        idempotency_key = _build_idempotency_key(
            event_id=normalized_event_id,
            message_id=normalized_message_id,
        )
        if idempotency_key is None:
            return IdempotencyDecision(is_duplicate=False, idempotency_key=None)

        async with self._session_factory() as session:
            insert_stmt = (
                pg_insert(ProcessedWebhookEvent)
                .values(
                    event_id=normalized_event_id,
                    message_id=normalized_message_id,
                    session_id=normalized_session_id,
                    contact_phone=normalized_contact_phone,
                )
                .on_conflict_do_nothing()
                .returning(ProcessedWebhookEvent.id)
            )
            result = await session.execute(insert_stmt)
            inserted_id = result.scalar_one_or_none()
            await session.commit()

        return IdempotencyDecision(
            is_duplicate=inserted_id is None,
            idempotency_key=idempotency_key,
        )


def _build_idempotency_key(*, event_id: str | None, message_id: str | None) -> str | None:
    if event_id is not None:
        return f"event:{event_id}"
    if message_id is not None:
        return f"message:{message_id}"

    return None


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def _normalize_required(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} deve ser informado para idempotencia de webhook.")

    return normalized
