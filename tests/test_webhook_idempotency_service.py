"""Testes do servico de idempotencia por `event_id`/`message_id`."""

from dataclasses import dataclass
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql

from app.core.webhook_idempotency_service import WebhookIdempotencyService


@dataclass
class _FakeResult:
    """Resultado minimo para simular retorno de `session.execute`."""

    value: Any

    def scalar_one_or_none(self) -> Any:
        return self.value


class _FakeSession:
    """Sessao fake para validar statements executados no service."""

    def __init__(self, inserted_id: int | None) -> None:
        self.inserted_id = inserted_id
        self.executed_statements: list[Any] = []
        self.commit_called = False

    async def execute(self, statement: Any) -> _FakeResult:
        self.executed_statements.append(statement)
        return _FakeResult(self.inserted_id)

    async def commit(self) -> None:
        self.commit_called = True


class _FakeSessionContext:
    """Context manager async para simular `async with session_factory()`."""

    def __init__(self, session: _FakeSession) -> None:
        self._session = session

    async def __aenter__(self) -> _FakeSession:
        return self._session

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


def _compile_postgres(statement: Any) -> str:
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


@pytest.mark.asyncio
async def test_register_or_detect_duplicate_marks_event_as_new_when_insert_succeeds() -> None:
    """Registra evento inedito e retorna decisao de nao duplicado."""
    fake_session = _FakeSession(inserted_id=77)
    service = WebhookIdempotencyService(session_factory=lambda: _FakeSessionContext(fake_session))

    decision = await service.register_or_detect_duplicate(
        event_id="evt-1",
        message_id="msg-1",
        session_id="sessao-1",
        contact_phone="+5511999999999",
    )

    assert decision.is_duplicate is False
    assert decision.idempotency_key == "event:evt-1"
    assert fake_session.commit_called is True
    assert len(fake_session.executed_statements) == 1

    insert_sql = _compile_postgres(fake_session.executed_statements[0])
    assert "INSERT INTO processed_webhook_events" in insert_sql
    assert "ON CONFLICT DO NOTHING" in insert_sql


@pytest.mark.asyncio
async def test_register_or_detect_duplicate_marks_duplicate_when_insert_conflicts() -> None:
    """Retorna duplicado quando insert nao gera linha por conflito de chave unica."""
    fake_session = _FakeSession(inserted_id=None)
    service = WebhookIdempotencyService(session_factory=lambda: _FakeSessionContext(fake_session))

    decision = await service.register_or_detect_duplicate(
        event_id=None,
        message_id="msg-dup",
        session_id="sessao-2",
        contact_phone="+5511888888888",
    )

    assert decision.is_duplicate is True
    assert decision.idempotency_key == "message:msg-dup"
    assert fake_session.commit_called is True


@pytest.mark.asyncio
async def test_register_or_detect_duplicate_skips_db_when_no_identifiers_exist() -> None:
    """Ignora idempotencia quando evento nao traz `event_id` nem `message_id`."""
    fake_session = _FakeSession(inserted_id=1)
    service = WebhookIdempotencyService(session_factory=lambda: _FakeSessionContext(fake_session))

    decision = await service.register_or_detect_duplicate(
        event_id=None,
        message_id=None,
        session_id="sessao-3",
        contact_phone="+5511777777777",
    )

    assert decision.is_duplicate is False
    assert decision.idempotency_key is None
    assert fake_session.commit_called is False
    assert fake_session.executed_statements == []
