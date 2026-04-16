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

    async def upsert(self, phone: str, session_id: str) -> Lead:
        """Insere lead sem duplicar telefone e atualiza `session_id` quando necessario."""
        async with self._session_factory() as session:
            # Primeiro passo: cria o lead caso ainda nao exista para este telefone.
            await session.execute(
                pg_insert(Lead)
                .values(phone=phone, session_id=session_id)
                .on_conflict_do_nothing(index_elements=[Lead.phone])
            )

            # Segundo passo: sincroniza `session_id` caso o lead ja existisse com sessao antiga.
            await session.execute(
                update(Lead)
                .where(Lead.phone == phone)
                .where(Lead.session_id != session_id)
                .values(session_id=session_id, updated_at=func.now())
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
