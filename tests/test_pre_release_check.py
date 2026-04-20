"""
Testes para o script de pre-release check.
"""

from pathlib import Path


def test_pre_release_script_exists():
    """Valida que o script de pre-release check existe."""
    script_path = Path("scripts/pre_release_check.py")
    assert script_path.exists(), "Script pre_release_check.py deve existir"
    assert script_path.is_file(), "pre_release_check.py deve ser um arquivo"


def test_pre_release_script_is_executable():
    """Valida que o script e executavel."""
    script_path = Path("scripts/pre_release_check.py")
    assert script_path.stat().st_mode & 0o111, "Script deve ser executavel"


def test_release_checklist_exists():
    """Valida que o checklist de release existe."""
    checklist_path = Path("docs/release-checklist.md")
    assert checklist_path.exists(), "Checklist de release deve existir"
    assert checklist_path.is_file(), "release-checklist.md deve ser um arquivo"


def test_release_checklist_has_required_sections():
    """Valida que o checklist tem todas as secoes obrigatorias."""
    checklist_path = Path("docs/release-checklist.md")
    content = checklist_path.read_text()
    
    required_sections = [
        "1. Qualidade de Codigo",
        "2. Seguranca",
        "3. Banco de Dados",
        "4. Documentacao",
        "5. Build e Deploy",
        "6. Integracao",
        "7. CI/CD",
        "8. Template",
    ]
    
    for section in required_sections:
        assert section in content, f"Secao '{section}' deve estar no checklist"


def test_fase_10_documentation_exists():
    """Valida que a documentacao da fase 10 existe."""
    fase_path = Path("docs/phases/fase-10.md")
    assert fase_path.exists(), "Documentacao da fase 10 deve existir"


def test_feature_10_1_documentation_exists():
    """Valida que a documentacao da feature 10.1 existe."""
    feature_path = Path("docs/features/fase-10-f10.1.md")
    assert feature_path.exists(), "Documentacao da feature 10.1 deve existir"


def test_feature_10_1_has_checklist_reference():
    """Valida que a feature 10.1 referencia o checklist."""
    feature_path = Path("docs/features/fase-10-f10.1.md")
    content = feature_path.read_text()
    
    assert "checklist" in content.lower(), "Feature deve mencionar checklist"
    assert "pre_release_check.py" in content, "Feature deve mencionar o script"
