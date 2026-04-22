"""Servico de persistencia de leads com operacoes async focadas em idempotencia."""

from collections.abc import Callable
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert

from db.models import Lead
from db.session import AsyncSessionLocal

SessionFactory = Callable[[], Any]


class LeadService:
    """Encapsula regras de escrita/leitura da tabela `leads`."""

    def __init__(self, session_factory: SessionFactory = AsyncSessionLocal) -> None:
        """Recebe fabrica de sessao para facilitar teste e injecao em runtime."""
        self._session_factory = session_factory

    async def upsert(self, phone: str, session_id: str, *, agent_session_id: str) -> Lead:
        """Insere lead sem duplicar telefone e sincroniza sessoes de canal e agente."""
        async with self._session_factory() as session:
            # Primeiro passo: cria o lead caso ainda nao exista para este telefone.
            await session.execute(
                pg_insert(Lead)
                .values(
                    phone=phone,
                    session_id=session_id,
                    agent_session_id=agent_session_id,
                )
                .on_conflict_do_nothing(index_elements=[Lead.phone])
            )

            # Segundo passo: sincroniza sessoes caso o lead ja existisse com valores antigos.
            await session.execute(
                update(Lead)
                .where(Lead.phone == phone)
                .where((Lead.session_id != session_id) | (Lead.agent_session_id != agent_session_id))
                .values(
                    session_id=session_id,
                    agent_session_id=agent_session_id,
                    updated_at=func.now(),
                )
            )

            await session.commit()

            result = await session.execute(select(Lead).where(Lead.phone == phone))
            lead = result.scalar_one_or_none()

        if lead is None:
            raise RuntimeError(f"Lead com telefone {phone} nao foi encontrado apos upsert.")

        return lead

    async def get_by_phone(self, phone: str) -> Lead | None:
        """Busca e retorna o lead completo a partir do telefone informado."""
        async with self._session_factory() as session:
            result = await session.execute(select(Lead).where(Lead.phone == phone))
            return result.scalar_one_or_none()

    async def update_metadata_by_phone(
        self,
        phone: str,
        *,
        crm_contact_id: str | None = None,
        status: str | None = None,
    ) -> None:
        """Persiste metadados operacionais (CRM/status) para telefone informado."""
        normalized_phone = phone.strip()
        if not normalized_phone:
            raise ValueError("phone deve ser informado para atualizar metadados do lead.")

        values: dict[str, Any] = {"updated_at": func.now()}
        normalized_crm_contact_id = _normalize_optional(crm_contact_id)
        normalized_status = _normalize_optional(status)
        if normalized_crm_contact_id is not None:
            values["crm_contact_id"] = normalized_crm_contact_id
        if normalized_status is not None:
            values["status"] = normalized_status

        if len(values) == 1:
            return

        async with self._session_factory() as session:
            await session.execute(update(Lead).where(Lead.phone == normalized_phone).values(**values))
            await session.commit()


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None
