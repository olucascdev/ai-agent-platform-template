"""
Testes para validar pipeline de release.
"""

import re
from pathlib import Path


def test_release_workflow_exists():
    """Valida que o workflow de release existe."""
    workflow_path = Path(".github/workflows/release.yml")
    assert workflow_path.exists(), "Workflow release.yml deve existir"
    assert workflow_path.is_file(), "release.yml deve ser um arquivo"


def test_pre_release_workflow_exists():
    """Valida que o workflow de pre-release existe."""
    workflow_path = Path(".github/workflows/pre-release.yml")
    assert workflow_path.exists(), "Workflow pre-release.yml deve existir"
    assert workflow_path.is_file(), "pre-release.yml deve ser um arquivo"


def test_extract_release_notes_script_exists():
    """Valida que o script de extracao de release notes existe."""
    script_path = Path("scripts/extract_release_notes.py")
    assert script_path.exists(), "Script extract_release_notes.py deve existir"
    assert script_path.is_file(), "extract_release_notes.py deve ser um arquivo"


def test_extract_release_notes_script_is_executable():
    """Valida que o script de extracao e executavel."""
    script_path = Path("scripts/extract_release_notes.py")
    assert script_path.stat().st_mode & 0o111, "Script extract_release_notes.py deve ser executavel"


def test_release_workflow_has_required_jobs():
    """Valida que o workflow de release tem jobs obrigatorios."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    required_jobs = [
        "validate:",
        "create-release:",
    ]
    
    for job in required_jobs:
        assert job in content, f"Job '{job}' deve estar no workflow de release"


def test_release_workflow_validates_quality():
    """Valida que o workflow de release executa validacoes de qualidade."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    validations = [
        "ruff check",
        "mypy",
        "pytest",
        "check_secrets_policy.py",
        "pre_release_check.py",
    ]
    
    for validation in validations:
        assert validation in content, f"Validacao '{validation}' deve estar no workflow"


def test_release_workflow_extracts_release_notes():
    """Valida que o workflow extrai release notes do CHANGELOG."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    assert "extract_release_notes.py" in content, "Workflow deve extrair release notes"
    assert "release_notes.md" in content, "Workflow deve gerar arquivo de release notes"


def test_release_workflow_creates_github_release():
    """Valida que o workflow cria release no GitHub."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    assert "softprops/action-gh-release" in content or "actions/create-release" in content, \
        "Workflow deve criar release no GitHub"


def test_release_workflow_triggers_on_tags():
    """Valida que o workflow e acionado por tags."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    assert "tags:" in content, "Workflow deve ser acionado por tags"
    assert "v*.*.*" in content or "v[0-9]" in content, "Workflow deve aceitar tags de versao"


def test_pre_release_workflow_validates_version_consistency():
    """Valida que o workflow de pre-release valida consistencia de versao."""
    workflow_path = Path(".github/workflows/pre-release.yml")
    content = workflow_path.read_text()
    
    checks = [
        "VERSION",
        "pyproject.toml",
        "CHANGELOG.md",
    ]
    
    for check in checks:
        assert check in content, f"Pre-release deve validar '{check}'"


def test_pre_release_workflow_comments_on_pr():
    """Valida que o workflow de pre-release comenta no PR."""
    workflow_path = Path(".github/workflows/pre-release.yml")
    content = workflow_path.read_text()
    
    assert "github-script" in content or "actions/github-script" in content, \
        "Workflow deve comentar no PR"


def test_extract_release_notes_script_has_usage():
    """Valida que o script de extracao tem instrucoes de uso."""
    script_path = Path("scripts/extract_release_notes.py")
    content = script_path.read_text()
    
    assert "Usage:" in content, "Script deve ter instrucoes de uso"
    assert "extract_release_notes" in content, "Script deve ter funcao principal"


def test_feature_10_4_documentation_exists():
    """Valida que a documentacao da feature 10.4 existe."""
    feature_path = Path("docs/features/fase-10-f10.4.md")
    assert feature_path.exists(), "Documentacao da feature 10.4 deve existir"


def test_release_workflow_has_permissions():
    """Valida que o workflow de release tem permissoes corretas."""
    workflow_path = Path(".github/workflows/release.yml")
    content = workflow_path.read_text()
    
    assert "permissions:" in content, "Workflow deve declarar permissoes"
    assert "contents: write" in content, "Workflow deve ter permissao de escrita"


def test_workflows_use_correct_python_version():
    """Valida que workflows usam versao correta do Python."""
    workflows = [
        ".github/workflows/release.yml",
        ".github/workflows/pre-release.yml",
    ]
    
    for workflow_path in workflows:
        path = Path(workflow_path)
        content = path.read_text()
        
        assert "python-version:" in content, f"{workflow_path} deve especificar versao do Python"
        assert "'3.12'" in content or "3.12" in content, \
            f"{workflow_path} deve usar Python 3.12"


def test_workflows_use_uv():
    """Valida que workflows usam uv para gerenciar dependencias."""
    workflows = [
        ".github/workflows/release.yml",
        ".github/workflows/pre-release.yml",
    ]
    
    for workflow_path in workflows:
        path = Path(workflow_path)
        content = path.read_text()
        
        assert "uv" in content, f"{workflow_path} deve usar uv"
        assert "uv sync" in content or "uv run" in content, \
            f"{workflow_path} deve instalar dependencias com uv"
