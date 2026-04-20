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


def test_phase_7_3_migration_contains_processed_events_table_creation() -> None:
    """Garante que migration da fase 7.3 cria tabela de idempotencia do webhook."""
    migration_file = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "versions"
        / "20260420_0002_create_processed_webhook_events_table.py"
    )
    content = migration_file.read_text(encoding="utf-8")

    assert "op.create_table(" in content
    assert '"processed_webhook_events"' in content
    assert "uq_processed_webhook_events_event_id" in content
    assert "uq_processed_webhook_events_message_id" in content


def test_phase_7_5_migration_contains_leads_status_column() -> None:
    """Garante migration que adiciona status operacional na tabela `leads`."""
    migration_file = (
        Path(__file__).resolve().parents[1] / "migrations" / "versions" / "20260420_0003_add_status_to_leads.py"
    )
    content = migration_file.read_text(encoding="utf-8")

    assert "op.add_column" in content
    assert '"leads"' in content
    assert '"status"' in content
    assert "ix_leads_status" in content
