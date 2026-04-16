"""Testes de contrato da migration inicial do banco."""

from pathlib import Path


def test_initial_migration_contains_leads_table_creation() -> None:
    """Garante que a migration inicial cria a tabela `leads` com constraint de telefone unico."""
    migration_file = (
        Path(__file__).resolve().parents[1] / "migrations" / "versions" / "20260416_0001_create_leads_table.py"
    )
    content = migration_file.read_text(encoding="utf-8")

    assert "op.create_table(" in content
    assert '"leads"' in content
    assert "uq_leads_phone" in content


def test_alembic_ini_points_to_migrations_directory() -> None:
    """Confirma que o Alembic esta configurado para usar a pasta `migrations`."""
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    content = alembic_ini.read_text(encoding="utf-8")

    assert "script_location = migrations" in content
