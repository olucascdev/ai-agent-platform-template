"""Utilitarios para URLs de banco com suporte a Supabase, Neon e Postgres local."""

from os import getenv
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

MANAGED_POSTGRES_HOST_MARKERS = ("supabase.co", "neon.tech")


def is_managed_postgres_url(database_url: str) -> bool:
    """Identifica se a URL aponta para provedor gerenciado (Supabase/Neon)."""
    hostname = (urlsplit(database_url).hostname or "").lower()
    return any(hostname.endswith(marker) for marker in MANAGED_POSTGRES_HOST_MARKERS)


def ensure_sslmode_for_managed_databases(database_url: str) -> str:
    """Garante `sslmode=require` para provedores gerenciados quando o parametro nao existe."""
    if not is_managed_postgres_url(database_url):
        return database_url

    parts = urlsplit(database_url)
    query_params = dict(parse_qsl(parts.query, keep_blank_values=True))

    if "sslmode" in query_params:
        return database_url

    query_params["sslmode"] = "require"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query_params), parts.fragment))


def to_async_database_url(database_url: str) -> str:
    """Normaliza a URL para runtime async com driver `asyncpg`."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url

    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return database_url


def to_sync_database_url(database_url: str) -> str:
    """Normaliza a URL para contexto sync (Alembic e tarefas administrativas)."""
    if database_url.startswith("postgresql+asyncpg://"):
        return database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    if database_url.startswith("postgresql+psycopg://"):
        return database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)

    return database_url


def resolve_runtime_database_url(database_url: str) -> str:
    """Resolve URL final de runtime (async + SSL em provedores gerenciados)."""
    async_url = to_async_database_url(database_url)
    return ensure_sslmode_for_managed_databases(async_url)


def resolve_migrations_database_url(database_url: str, database_url_migrations: str | None = None) -> str:
    """Resolve URL final de migrations priorizando URL dedicada quando informada."""
    base_url = database_url_migrations or database_url
    sync_url = to_sync_database_url(base_url)
    return ensure_sslmode_for_managed_databases(sync_url)


def build_sqlalchemy_engine_kwargs(database_url: str) -> dict[str, Any]:
    """Retorna kwargs padrao para engine SQLAlchemy com foco em resiliencia."""
    kwargs: dict[str, Any] = {"pool_pre_ping": True}

    if is_managed_postgres_url(database_url):
        kwargs["pool_recycle"] = 300

    return kwargs


# Compatibilidade temporaria com modulos antigos que importam `db_url`.
db_url = resolve_runtime_database_url(getenv("DATABASE_URL", "postgresql+asyncpg://ai:ai@localhost:5432/ai"))
