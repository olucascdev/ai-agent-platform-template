"""Contexto de correlation id para rastreamento de requests."""

from contextvars import ContextVar, Token
from uuid import uuid4

_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Retorna correlation id ativo no contexto atual."""
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> Token[str | None]:
    """Define correlation id no contexto atual e retorna token de reset."""
    return _correlation_id_ctx.set(correlation_id)


def reset_correlation_id(token: Token[str | None]) -> None:
    """Restaura valor anterior de correlation id no contexto."""
    _correlation_id_ctx.reset(token)


def resolve_correlation_id(header_value: str | None) -> str:
    """Resolve correlation id a partir de header ou gera valor novo."""
    if header_value is not None:
        normalized = header_value.strip()
        if normalized:
            return normalized

    return uuid4().hex
