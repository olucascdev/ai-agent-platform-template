"""Testes do LeadService com foco em contrato de queries e retorno."""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.dialects import postgresql

from app.core.lead_service import LeadService


@dataclass
class _FakeResult:
    """Resultado minimo para simular `scalar_one_or_none` do SQLAlchemy."""

    value: Any

    def scalar_one_or_none(self) -> Any:
        """Retorna valor configurado para o cenario de teste."""
        return self.value


class _FakeSession:
    """Sessao fake para registrar statements executados pelo service."""

    def __init__(self, selected_lead: Any) -> None:
        self.selected_lead = selected_lead
        self.executed_statements: list[Any] = []
        self.commit_called = False

    async def execute(self, statement: Any) -> _FakeResult:
        """Registra query recebida e responde lead no select final."""
        self.executed_statements.append(statement)

        statement_type = statement.__class__.__name__.lower()
        if "select" in statement_type:
            return _FakeResult(self.selected_lead)

        return _FakeResult(None)

    async def commit(self) -> None:
        """Marca que houve commit da transacao."""
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
    """Compila statement para SQL PostgreSQL em string de validacao."""
    return str(statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


@pytest.mark.asyncio
async def test_upsert_executes_insert_update_select_sequence() -> None:
    """Garante o fluxo `insert do nothing` -> `update` -> `select` no upsert."""
    expected_lead = SimpleNamespace(
        phone="+5511999999999",
        session_id="session_payload_123",
        agent_session_id="tenant_abc",
    )
    fake_session = _FakeSession(selected_lead=expected_lead)
    service = LeadService(session_factory=lambda: _FakeSessionContext(fake_session))

    lead = await service.upsert(
        phone="+5511999999999",
        session_id="session_payload_123",
        agent_session_id="tenant_abc",
    )

    assert lead is expected_lead
    assert fake_session.commit_called is True
    assert len(fake_session.executed_statements) == 3

    insert_sql = _compile_postgres(fake_session.executed_statements[0])
    update_sql = _compile_postgres(fake_session.executed_statements[1])
    select_sql = _compile_postgres(fake_session.executed_statements[2])

    assert "INSERT INTO leads" in insert_sql
    assert "ON CONFLICT (phone) DO NOTHING" in insert_sql
    assert "UPDATE leads" in update_sql
    assert "session_id" in update_sql
    assert "agent_session_id" in update_sql
    assert "SELECT" in select_sql
    assert "FROM leads" in select_sql


@pytest.mark.asyncio
async def test_upsert_raises_when_lead_is_not_returned() -> None:
    """Confirma erro claro quando o lead nao e encontrado apos o upsert."""
    fake_session = _FakeSession(selected_lead=None)
    service = LeadService(session_factory=lambda: _FakeSessionContext(fake_session))

    with pytest.raises(RuntimeError) as exc_info:
        await service.upsert(
            phone="+5511888888888",
            session_id="session_payload_xyz",
            agent_session_id="tenant_xyz",
        )

    assert "nao foi encontrado apos upsert" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_by_phone_returns_lead_without_commit() -> None:
    """Valida consulta simples por telefone sem efeito colateral de commit."""
    expected_lead = SimpleNamespace(
        phone="+5511777777777",
        session_id="session_payload_mno",
        agent_session_id="tenant_mno",
    )
    fake_session = _FakeSession(selected_lead=expected_lead)
    service = LeadService(session_factory=lambda: _FakeSessionContext(fake_session))

    lead = await service.get_by_phone(phone="+5511777777777")

    assert lead is expected_lead
    assert fake_session.commit_called is False
    assert len(fake_session.executed_statements) == 1


@pytest.mark.asyncio
async def test_update_metadata_by_phone_updates_crm_contact_id_and_status() -> None:
    """Persiste metadados operacionais no lead quando valores sao informados."""
    fake_session = _FakeSession(selected_lead=None)
    service = LeadService(session_factory=lambda: _FakeSessionContext(fake_session))

    await service.update_metadata_by_phone(
        "+5511666666666",
        crm_contact_id="crm-700",
        status="message_sent",
    )

    assert fake_session.commit_called is True
    assert len(fake_session.executed_statements) == 1

    update_sql = _compile_postgres(fake_session.executed_statements[0])
    assert "UPDATE leads" in update_sql
    assert "crm_contact_id='crm-700'" in update_sql
    assert "status='message_sent'" in update_sql


@pytest.mark.asyncio
async def test_update_metadata_by_phone_skips_when_only_empty_values_are_provided() -> None:
    """Evita update/commit quando nao ha metadados validos para persistir."""
    fake_session = _FakeSession(selected_lead=None)
    service = LeadService(session_factory=lambda: _FakeSessionContext(fake_session))

    await service.update_metadata_by_phone("+5511555555555", crm_contact_id=" ", status="")

    assert fake_session.executed_statements == []
    assert fake_session.commit_called is False
