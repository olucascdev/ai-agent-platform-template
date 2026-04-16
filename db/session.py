"""Sessao async do SQLAlchemy com configuracao compartilhada da aplicacao."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

DEFAULT_ENGINE_KWARGS = settings.sqlalchemy_engine_kwargs


def create_async_engine_for_runtime() -> AsyncEngine:
    """Cria engine async principal usando a URL normalizada do runtime."""
    return create_async_engine(settings.runtime_database_url, **DEFAULT_ENGINE_KWARGS)


async_engine = create_async_engine_for_runtime()

# Fabrica padrao de sessoes assicronas usada por services e repositorios.
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornece sessao async por request/escopo e garante fechamento ao final."""
    async with AsyncSessionLocal() as session:
        yield session
