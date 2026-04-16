"""Testes para estrategia de URL de banco multi-provider."""

from db.url import (
    build_sqlalchemy_engine_kwargs,
    resolve_migrations_database_url,
    resolve_runtime_database_url,
)


def test_runtime_url_is_converted_to_async_driver() -> None:
    """Garante que URLs genericas sejam normalizadas para `postgresql+asyncpg`."""
    runtime_url = resolve_runtime_database_url("postgresql://user:pass@localhost:5432/app")

    assert runtime_url.startswith("postgresql+asyncpg://")


def test_migrations_url_fallback_converts_to_async_driver() -> None:
    """Confirma que o fallback de migrations mantem driver async compativel."""
    migrations_url = resolve_migrations_database_url("postgresql+asyncpg://user:pass@localhost:5432/app")

    assert migrations_url.startswith("postgresql+asyncpg://")


def test_migrations_url_prefers_explicit_dedicated_value() -> None:
    """Valida que a URL dedicada de migration tem prioridade quando informada."""
    migrations_url = resolve_migrations_database_url(
        database_url="postgresql+asyncpg://user:pass@localhost:5432/app",
        database_url_migrations="postgresql://admin:secret@localhost:5432/app",
    )

    assert migrations_url == "postgresql+asyncpg://admin:secret@localhost:5432/app"


def test_managed_provider_url_receives_sslmode_when_missing() -> None:
    """Assegura `sslmode=require` automaticamente para Supabase/Neon."""
    runtime_url = resolve_runtime_database_url("postgresql://u:p@db.abcd.supabase.co:5432/postgres")

    assert "sslmode=require" in runtime_url


def test_engine_kwargs_include_pool_recycle_for_managed_provider() -> None:
    """Garante ajustes extras de pool para provedores gerenciados."""
    managed_kwargs = build_sqlalchemy_engine_kwargs("postgresql+asyncpg://u:p@ep.neon.tech:5432/app")
    local_kwargs = build_sqlalchemy_engine_kwargs("postgresql+asyncpg://u:p@localhost:5432/app")

    assert managed_kwargs["pool_pre_ping"] is True
    assert managed_kwargs["pool_recycle"] == 300
    assert local_kwargs == {"pool_pre_ping": True}
