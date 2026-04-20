#!/usr/bin/env python3
"""
Script para extrair release notes do CHANGELOG.md.

Usage:
    python scripts/extract_release_notes.py 1.2.3
    python scripts/extract_release_notes.py 1.2.3 --output release_notes.md
"""

import re
import sys
from pathlib import Path


def extract_release_notes(version: str, changelog_path: Path = Path("CHANGELOG.md")) -> str:
    """
    Extrai release notes para uma versao especifica do CHANGELOG.md.
    
    Args:
        version: Versao para extrair (ex: "1.2.3")
        changelog_path: Caminho para o CHANGELOG.md
        
    Returns:
        Release notes como string
    """
    if not changelog_path.exists():
        raise FileNotFoundError(f"CHANGELOG.md not found at {changelog_path}")
    
    content = changelog_path.read_text()
    
    # Padrao para encontrar a secao da versao
    # Formato: ## [1.2.3] - 2026-04-20
    version_pattern = rf"## \[{re.escape(version)}\].*?\n(.*?)(?=\n## \[|\Z)"
    
    match = re.search(version_pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError(f"Version {version} not found in CHANGELOG.md")
    
    release_notes = match.group(1).strip()
    
    if not release_notes:
        raise ValueError(f"No release notes found for version {version}")
    
    return release_notes


def format_release_notes(version: str, notes: str) -> str:
    """
    Formata release notes para GitHub Release.
    
    Args:
        version: Versao da release
        notes: Release notes extraidas do CHANGELOG
        
    Returns:
        Release notes formatadas
    """
    header = f"# Release v{version}\n\n"
    
    # Adicionar link para changelog completo
    footer = "\n\n---\n\n"
    footer += "## Full Changelog\n\n"
    footer += f"See [CHANGELOG.md](CHANGELOG.md) for complete history.\n"
    
    return header + notes + footer


def main() -> int:
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_release_notes.py VERSION [--output FILE]")
        print("\nExamples:")
        print("  python scripts/extract_release_notes.py 1.2.3")
        print("  python scripts/extract_release_notes.py 1.2.3 --output release_notes.md")
        return 1
    
    version = sys.argv[1]
    
    # Parse output option
    output_file = None
    if len(sys.argv) >= 4 and sys.argv[2] == "--output":
        output_file = Path(sys.argv[3])
    
    try:
        # Extract release notes
        notes = extract_release_notes(version)
        
        # Format for GitHub
        formatted_notes = format_release_notes(version, notes)
        
        # Output
        if output_file:
            output_file.write_text(formatted_notes)
            print(f"Release notes written to {output_file}", file=sys.stderr)
        else:
            print(formatted_notes)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("\nMake sure CHANGELOG.md has an entry for version {version}", file=sys.stderr)
        print("Format: ## [{version}] - YYYY-MM-DD", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
