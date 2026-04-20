"""Testes da politica de segredos para codigo e workflows (fase 8.3)."""

from pathlib import Path

from app.security import scan_repository_for_secret_policy_violations, scan_text_for_secret_policy_violations


def test_scan_text_flags_hardcoded_secret_in_workflow() -> None:
    """Detecta valor literal para variavel de segredo em workflow."""
    workflow_text = "OPENAI_API_KEY: hardcoded-value"

    violations = scan_text_for_secret_policy_violations(Path(".github/workflows/validate.yml"), workflow_text)

    assert len(violations) == 1
    assert violations[0].rule == "workflow_secret_literal"


def test_scan_text_allows_workflow_secret_expression() -> None:
    """Permite uso de segredo via expressao `${{ secrets.* }}` no workflow."""
    workflow_text = "OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}"

    violations = scan_text_for_secret_policy_violations(Path(".github/workflows/validate.yml"), workflow_text)

    assert violations == []


def test_scan_text_flags_hardcoded_secret_assignment_in_code() -> None:
    """Detecta assignment literal de segredo em codigo Python."""
    code_text = 'OPENAI_API_KEY = "hardcoded-value"'

    violations = scan_text_for_secret_policy_violations(Path("app/example.py"), code_text)

    assert len(violations) == 1
    assert violations[0].rule == "code_secret_literal"


def test_repository_has_no_secret_policy_violations() -> None:
    """Repositorio deve respeitar politica de segredos sem hardcodes."""
    repo_root = Path(__file__).resolve().parents[1]

    violations = scan_repository_for_secret_policy_violations(repo_root)

    assert violations == []
