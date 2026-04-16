"""
Database Module
---------------

Database connection utilities.
"""

from db.url import (
    build_sqlalchemy_engine_kwargs,
    db_url,
    resolve_migrations_database_url,
    resolve_runtime_database_url,
)


def get_postgres_db(contents_table: str | None = None):
    """Wrapper lazy para manter compatibilidade sem carregar dependencias pesadas no import."""
    from db.session import get_postgres_db as _get_postgres_db

    return _get_postgres_db(contents_table)


def create_knowledge(name: str, table_name: str):
    """Wrapper lazy para manter compatibilidade da API publica de `db`."""
    from db.session import create_knowledge as _create_knowledge

    return _create_knowledge(name, table_name)


__all__ = [
    "build_sqlalchemy_engine_kwargs",
    "create_knowledge",
    "db_url",
    "get_postgres_db",
    "resolve_migrations_database_url",
    "resolve_runtime_database_url",
]
