#!/usr/bin/env python3
"""Valida politica de segredos: sem hardcodes em codigo e workflow."""

from pathlib import Path
import sys

from app.security import scan_repository_for_secret_policy_violations


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    violations = scan_repository_for_secret_policy_violations(repo_root)
    if not violations:
        print("Secrets policy check passed.")
        return 0

    print("Secrets policy violations found:")
    for violation in violations:
        print(
            f"- {violation.file_path}:{violation.line_number} "
            f"[{violation.rule}] {violation.message} | {violation.snippet}"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
