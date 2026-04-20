#!/usr/bin/env python3
"""
Script para atualizar versao do template.

Usage:
    python scripts/bump_version.py patch    # 1.0.0 -> 1.0.1
    python scripts/bump_version.py minor    # 1.0.0 -> 1.1.0
    python scripts/bump_version.py major    # 1.0.0 -> 2.0.0
    python scripts/bump_version.py 1.2.3    # Define versao especifica
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def parse_version(version: str) -> Tuple[int, int, int]:
    """Parse version string to tuple."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version.strip())
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return tuple(map(int, match.groups()))


def format_version(major: int, minor: int, patch: int) -> str:
    """Format version tuple to string."""
    return f"{major}.{minor}.{patch}"


def get_current_version() -> str:
    """Get current version from VERSION file."""
    version_file = Path("VERSION")
    if not version_file.exists():
        raise FileNotFoundError("VERSION file not found")
    return version_file.read_text().strip()


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type."""
    major, minor, patch = parse_version(current)
    
    if bump_type == "major":
        return format_version(major + 1, 0, 0)
    elif bump_type == "minor":
        return format_version(major, minor + 1, 0)
    elif bump_type == "patch":
        return format_version(major, minor, patch + 1)
    else:
        # Assume it's a specific version
        parse_version(bump_type)  # Validate format
        return bump_type


def update_version_file(new_version: str) -> None:
    """Update VERSION file."""
    version_file = Path("VERSION")
    version_file.write_text(new_version + "\n")
    print(f"✓ Updated VERSION: {new_version}")


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        print("⚠ pyproject.toml not found, skipping")
        return
    
    content = pyproject_file.read_text()
    
    # Update version in [project] section
    updated = re.sub(
        r'(version\s*=\s*")[^"]+(")',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    
    if updated == content:
        print("⚠ Version not found in pyproject.toml")
        return
    
    pyproject_file.write_text(updated)
    print(f"✓ Updated pyproject.toml: {new_version}")


def update_changelog(old_version: str, new_version: str) -> None:
    """Update CHANGELOG.md with new version."""
    changelog_file = Path("CHANGELOG.md")
    if not changelog_file.exists():
        print("⚠ CHANGELOG.md not found, skipping")
        return
    
    content = changelog_file.read_text()
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Replace [Unreleased] with new version
    updated = content.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n### Em desenvolvimento\n- TBD\n\n## [{new_version}] - {today}"
    )
    
    if updated == content:
        print("⚠ [Unreleased] section not found in CHANGELOG.md")
        return
    
    changelog_file.write_text(updated)
    print(f"✓ Updated CHANGELOG.md: [{new_version}] - {today}")


def main() -> int:
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/bump_version.py [major|minor|patch|X.Y.Z]")
        print("\nExamples:")
        print("  python scripts/bump_version.py patch    # 1.0.0 -> 1.0.1")
        print("  python scripts/bump_version.py minor    # 1.0.0 -> 1.1.0")
        print("  python scripts/bump_version.py major    # 1.0.0 -> 2.0.0")
        print("  python scripts/bump_version.py 1.2.3    # Set specific version")
        return 1
    
    bump_type = sys.argv[1]
    
    try:
        # Get current version
        current_version = get_current_version()
        print(f"Current version: {current_version}")
        
        # Calculate new version
        new_version = bump_version(current_version, bump_type)
        print(f"New version: {new_version}")
        
        # Confirm
        response = input(f"\nUpdate version from {current_version} to {new_version}? [y/N] ")
        if response.lower() != "y":
            print("Aborted.")
            return 0
        
        # Update files
        print("\nUpdating files...")
        update_version_file(new_version)
        update_pyproject_toml(new_version)
        update_changelog(current_version, new_version)
        
        print(f"\n✓ Version bumped successfully: {current_version} -> {new_version}")
        print("\nNext steps:")
        print("1. Review changes: git diff")
        print("2. Update CHANGELOG.md with release notes")
        print("3. Commit changes: git add -A && git commit -m 'chore: bump version to {}'".format(new_version))
        print("4. Create tag: git tag -a v{} -m 'Release v{}'".format(new_version, new_version))
        print("5. Push: git push && git push --tags")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
