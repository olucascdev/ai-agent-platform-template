"""Contratos do workflow CI para validacao de migrations (fase 8.5)."""

from pathlib import Path


def _read_validate_workflow() -> str:
    workflow_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "validate.yml"
    return workflow_path.read_text(encoding="utf-8")


def test_validate_workflow_provisions_postgres_service_for_migration_check() -> None:
    """Workflow deve subir Postgres para executar migracoes de verdade no CI."""
    content = _read_validate_workflow()

    assert "services:" in content
    assert "postgres:" in content
    assert "image: postgres:16-alpine" in content
    assert "POSTGRES_USER: ai" in content
    assert "DATABASE_URL_MIGRATIONS" in content


def test_validate_workflow_runs_alembic_upgrade_and_downgrade_steps() -> None:
    """Workflow deve validar subida e descida de migration no banco de CI."""
    content = _read_validate_workflow()

    assert "Validate migrations in CI database" in content
    assert "uv run alembic upgrade head" in content
    assert "uv run alembic downgrade base" in content
