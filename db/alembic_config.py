"""Helpers de configuracao do Alembic sem depender dos settings completos da aplicacao."""

from os import getenv

from dotenv import load_dotenv
from sqlalchemy import MetaData

from db.base import Base
from db.url import resolve_migrations_database_url


def get_migrations_database_url() -> str:
    """Resolve a URL do Alembic priorizando `DATABASE_URL_MIGRATIONS`."""
    # Carrega `.env` para facilitar execucao local do Alembic via CLI.
    load_dotenv(override=False)

    database_url = getenv("DATABASE_URL", "postgresql+asyncpg://ai:ai@localhost:5432/ai")
    database_url_migrations = getenv("DATABASE_URL_MIGRATIONS")
    return resolve_migrations_database_url(database_url, database_url_migrations)


def get_target_metadata() -> MetaData:
    """Retorna metadata de modelos mapeados para autogenerate do Alembic."""
    # Import local para registrar modelos antes de expor `Base.metadata`.
    from db import models as _models

    _ = _models
    return Base.metadata
