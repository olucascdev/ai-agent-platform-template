"""
Testes para validar versionamento e changelog.
"""

import re
from pathlib import Path


def test_version_file_exists():
    """Valida que o arquivo VERSION existe."""
    version_file = Path("VERSION")
    assert version_file.exists(), "VERSION file deve existir"
    assert version_file.is_file(), "VERSION deve ser um arquivo"


def test_version_format_is_valid():
    """Valida que a versao tem formato valido (semver)."""
    version_file = Path("VERSION")
    version = version_file.read_text().strip()
    
    # Formato: X.Y.Z onde X, Y, Z sao numeros
    pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(pattern, version), f"Versao deve seguir formato X.Y.Z, encontrado: {version}"


def test_changelog_exists():
    """Valida que o CHANGELOG.md existe."""
    changelog_file = Path("CHANGELOG.md")
    assert changelog_file.exists(), "CHANGELOG.md deve existir"
    assert changelog_file.is_file(), "CHANGELOG.md deve ser um arquivo"


def test_changelog_has_required_sections():
    """Valida que o changelog tem secoes obrigatorias."""
    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()
    
    required_sections = [
        "# Changelog",
        "## [Unreleased]",
        "## [1.0.0]",
        "### Added",
    ]
    
    for section in required_sections:
        assert section in content, f"Secao '{section}' deve estar no CHANGELOG.md"


def test_changelog_follows_keep_a_changelog():
    """Valida que o changelog segue formato Keep a Changelog."""
    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()
    
    # Deve mencionar Keep a Changelog
    assert "Keep a Changelog" in content, "CHANGELOG deve mencionar Keep a Changelog"
    
    # Deve mencionar Semantic Versioning
    assert "Semantic Versioning" in content, "CHANGELOG deve mencionar Semantic Versioning"


def test_changelog_has_version_categories():
    """Valida que o changelog tem categorias de mudancas."""
    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()
    
    categories = [
        "### Added",
        "### Changed",
        "### Deprecated",
        "### Removed",
        "### Fixed",
        "### Security",
    ]
    
    # Pelo menos algumas categorias devem estar presentes
    found_categories = sum(1 for cat in categories if cat in content)
    assert found_categories >= 3, "CHANGELOG deve ter pelo menos 3 categorias de mudancas"


def test_version_in_pyproject_matches_version_file():
    """Valida que versao em pyproject.toml corresponde ao VERSION file."""
    version_file = Path("VERSION")
    version = version_file.read_text().strip()
    
    pyproject_file = Path("pyproject.toml")
    pyproject_content = pyproject_file.read_text()
    
    # Extrair versao do pyproject.toml
    match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
    assert match, "Versao nao encontrada em pyproject.toml"
    
    pyproject_version = match.group(1)
    assert version == pyproject_version, f"Versao em VERSION ({version}) deve corresponder a pyproject.toml ({pyproject_version})"


def test_bump_version_script_exists():
    """Valida que o script de bump de versao existe."""
    script_path = Path("scripts/bump_version.py")
    assert script_path.exists(), "Script bump_version.py deve existir"
    assert script_path.is_file(), "bump_version.py deve ser um arquivo"


def test_bump_version_script_is_executable():
    """Valida que o script de bump e executavel."""
    script_path = Path("scripts/bump_version.py")
    assert script_path.stat().st_mode & 0o111, "Script bump_version.py deve ser executavel"


def test_release_process_doc_exists():
    """Valida que a documentacao de processo de release existe."""
    doc_path = Path("docs/RELEASE_PROCESS.md")
    assert doc_path.exists(), "RELEASE_PROCESS.md deve existir"
    assert doc_path.is_file(), "RELEASE_PROCESS.md deve ser um arquivo"


def test_release_process_has_required_sections():
    """Valida que o processo de release tem secoes obrigatorias."""
    doc_path = Path("docs/RELEASE_PROCESS.md")
    content = doc_path.read_text()
    
    required_sections = [
        "Pre-requisitos",
        "Tipos de Release",
        "Processo Passo a Passo",
        "Checklist de Release",
        "Rollback",
    ]
    
    for section in required_sections:
        assert section in content, f"Secao '{section}' deve estar no RELEASE_PROCESS.md"


def test_release_process_documents_semver():
    """Valida que o processo de release documenta semantic versioning."""
    doc_path = Path("docs/RELEASE_PROCESS.md")
    content = doc_path.read_text()
    
    assert "MAJOR" in content, "Processo deve documentar MAJOR version"
    assert "MINOR" in content, "Processo deve documentar MINOR version"
    assert "PATCH" in content, "Processo deve documentar PATCH version"
    assert "Semantic Versioning" in content, "Processo deve mencionar Semantic Versioning"


def test_feature_10_3_documentation_exists():
    """Valida que a documentacao da feature 10.3 existe."""
    feature_path = Path("docs/features/fase-10-f10.3.md")
    assert feature_path.exists(), "Documentacao da feature 10.3 deve existir"


def test_changelog_has_current_version():
    """Valida que o changelog documenta a versao atual."""
    version_file = Path("VERSION")
    version = version_file.read_text().strip()
    
    changelog_file = Path("CHANGELOG.md")
    content = changelog_file.read_text()
    
    assert f"## [{version}]" in content, f"CHANGELOG deve documentar versao atual [{version}]"
