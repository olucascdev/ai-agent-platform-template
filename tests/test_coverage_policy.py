"""Testes de contrato da politica minima de cobertura (fase 8.4)."""

from pathlib import Path
import tomllib


def _load_pyproject() -> dict:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    return tomllib.loads(pyproject_path.read_text(encoding="utf-8"))


def test_pyproject_includes_pytest_cov_in_dev_dependencies() -> None:
    """Garante que `pytest-cov` esta disponivel no extra de desenvolvimento."""
    pyproject = _load_pyproject()
    dev_dependencies = pyproject["project"]["optional-dependencies"]["dev"]

    assert "pytest-cov" in dev_dependencies


def test_pytest_addopts_enforces_minimum_coverage_threshold() -> None:
    """Valida parametros de cobertura habilitados por padrao no pytest."""
    pyproject = _load_pyproject()
    addopts = pyproject["tool"]["pytest"]["ini_options"]["addopts"]

    assert "--cov=app" in addopts
    assert "--cov=db" in addopts
    assert "--cov-fail-under=85" in addopts


def test_coverage_report_section_defines_fail_under_policy() -> None:
    """Confirma politica declarativa de cobertura minima no tool.coverage.report."""
    pyproject = _load_pyproject()
    coverage_report = pyproject["tool"]["coverage"]["report"]

    assert coverage_report["fail_under"] == 85
