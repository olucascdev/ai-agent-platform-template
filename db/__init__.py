"""
Database Module
---------------

Database connection utilities.
"""

from db.base import Base
from db.models import Lead, ProcessedWebhookEvent
from db.url import (
    build_sqlalchemy_engine_kwargs,
    db_url,
    resolve_migrations_database_url,
    resolve_runtime_database_url,
)


def get_async_session():
    """Wrapper lazy para evitar import ciclico durante bootstrap de configuracao."""
    from db.session import get_async_session as _get_async_session

    return _get_async_session()


def get_async_session_local():
    """Retorna a fabrica de sessao async sem carregar `db.session` no import do pacote."""
    from db.session import AsyncSessionLocal as _async_session_local

    return _async_session_local


def get_async_engine():
    """Retorna engine async principal com import tardio para evitar ciclos."""
    from db.session import async_engine as _async_engine

    return _async_engine


__all__ = [
    "Base",
    "Lead",
    "ProcessedWebhookEvent",
    "build_sqlalchemy_engine_kwargs",
    "db_url",
    "get_async_engine",
    "get_async_session",
    "get_async_session_local",
    "resolve_migrations_database_url",
    "resolve_runtime_database_url",
]
