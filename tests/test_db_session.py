"""Testes da camada de sessao async do SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession

from db.session import AsyncSessionLocal, async_engine, get_async_session


def test_async_engine_uses_asyncpg_driver() -> None:
    """Valida que a engine de runtime usa driver async para a aplicacao."""
    assert async_engine.url.drivername == "postgresql+asyncpg"


def test_async_session_factory_uses_async_session_class() -> None:
    """Garante que a fabrica da sessao gera sessoes assicronas do SQLAlchemy."""
    assert AsyncSessionLocal.class_ is AsyncSession


async def test_get_async_session_yields_session_instance() -> None:
    """Confirma que o provider de sessao retorna um objeto `AsyncSession`."""
    session_generator = get_async_session()
    session = await anext(session_generator)

    assert isinstance(session, AsyncSession)
    await session_generator.aclose()
