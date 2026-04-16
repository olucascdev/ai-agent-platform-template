"""Testes de configuracao do Alembic para migrations do projeto."""

from db.alembic_config import get_migrations_database_url, get_target_metadata


def test_get_migrations_database_url_uses_dedicated_env_when_present(monkeypatch) -> None:
    """Garante prioridade de `DATABASE_URL_MIGRATIONS` quando a variavel existe."""
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/app")
    monkeypatch.setenv("DATABASE_URL_MIGRATIONS", "postgresql://admin:secret@localhost:5432/app")

    url = get_migrations_database_url()

    assert url == "postgresql+asyncpg://admin:secret@localhost:5432/app"


def test_get_target_metadata_includes_leads_table() -> None:
    """Valida que a metadata usada pelo Alembic enxerga a tabela `leads`."""
    metadata = get_target_metadata()

    assert "leads" in metadata.tables
