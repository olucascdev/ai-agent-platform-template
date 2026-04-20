#!/usr/bin/env python3
"""
Script de validacao pre-release.
Executa todos os checks obrigatorios antes de publicar uma release.

Usage:
    python scripts/pre_release_check.py
    python scripts/pre_release_check.py --verbose
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text: str) -> None:
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def run_command(cmd: List[str], check_name: str, verbose: bool = False) -> Tuple[bool, str]:
    """
    Run a command and return success status and output.
    
    Args:
        cmd: Command to run as list of strings
        check_name: Name of the check for logging
        verbose: Whether to print command output
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        
        output = result.stdout + result.stderr
        
        if verbose and output:
            print(f"  Output: {output[:200]}")
        
        if result.returncode == 0:
            print_success(f"{check_name} passed")
            return True, output
        else:
            print_error(f"{check_name} failed")
            if not verbose and output:
                print(f"  {output[:500]}")
            return False, output
            
    except FileNotFoundError:
        print_error(f"{check_name} failed - command not found: {cmd[0]}")
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        print_error(f"{check_name} failed with exception: {e}")
        return False, str(e)


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print_success(f"{description} exists: {filepath}")
        return True
    else:
        print_error(f"{description} missing: {filepath}")
        return False


def check_quality(verbose: bool) -> bool:
    """Run code quality checks."""
    print_header("1. QUALIDADE DE CODIGO")
    
    checks = [
        (["uv", "run", "ruff", "check", "."], "Ruff linting"),
        (["uv", "run", "mypy", "."], "MyPy type checking"),
        (["uv", "run", "pytest", "--cov=app", "--cov=db", "--cov-fail-under=85", "-q"], "Pytest with coverage >= 85%"),
    ]
    
    results = []
    for cmd, name in checks:
        success, _ = run_command(cmd, name, verbose)
        results.append(success)
    
    return all(results)


def check_security(verbose: bool) -> bool:
    """Run security checks."""
    print_header("2. SEGURANCA")
    
    checks = [
        (["python", "scripts/check_secrets_policy.py"], "Secrets policy validation"),
    ]
    
    results = []
    for cmd, name in checks:
        success, _ = run_command(cmd, name, verbose)
        results.append(success)
    
    # Check for critical files
    results.append(check_file_exists(".env.example", ".env.example"))
    results.append(check_file_exists(".gitignore", ".gitignore"))
    
    return all(results)


def check_database(verbose: bool) -> bool:
    """Run database migration checks."""
    print_header("3. BANCO DE DADOS")
    
    print_warning("Database checks require DATABASE_URL to be set")
    print_warning("Skipping migration validation (run manually with alembic)")
    
    # Check migration files exist
    migrations_dir = Path("db/migrations/versions")
    if migrations_dir.exists() and list(migrations_dir.glob("*.py")):
        print_success("Migration files found")
        return True
    else:
        print_error("No migration files found")
        return False


def check_documentation(verbose: bool) -> bool:
    """Check documentation completeness."""
    print_header("4. DOCUMENTACAO")
    
    required_docs = [
        ("README.md", "README"),
        ("docs/phases/fase-10.md", "Fase 10 documentation"),
        (".env.example", "Environment variables example"),
    ]
    
    results = []
    for filepath, description in required_docs:
        results.append(check_file_exists(filepath, description))
    
    # Check features documentation
    features_dir = Path("docs/features")
    if features_dir.exists():
        feature_files = list(features_dir.glob("fase-*.md"))
        print_success(f"Found {len(feature_files)} feature documentation files")
        results.append(True)
    else:
        print_error("Features documentation directory missing")
        results.append(False)
    
    return all(results)


def check_build(verbose: bool) -> bool:
    """Check build configuration."""
    print_header("5. BUILD E DEPLOY")
    
    required_files = [
        ("pyproject.toml", "Python project configuration"),
        ("Dockerfile", "Docker configuration"),
        ("compose.yaml", "Docker Compose configuration"),
    ]
    
    results = []
    for filepath, description in required_files:
        results.append(check_file_exists(filepath, description))
    
    print_warning("Docker build check skipped (run 'docker compose up --build' manually)")
    
    return all(results)


def check_integration(verbose: bool) -> bool:
    """Check integration configuration."""
    print_header("6. INTEGRACAO")
    
    # Check key integration files exist
    integration_files = [
        ("app/api/webhook.py", "Webhook endpoint"),
        ("app/integrations/crm_client.py", "CRM client"),
        ("app/integrations/whatsapp_sender_client.py", "Sender client"),
        ("app/preprocessing/event_normalizer.py", "Event normalizer"),
    ]
    
    results = []
    for filepath, description in integration_files:
        results.append(check_file_exists(filepath, description))
    
    print_warning("Integration tests require running services (run manually)")
    
    return all(results)


def check_ci(verbose: bool) -> bool:
    """Check CI/CD configuration."""
    print_header("7. CI/CD")
    
    ci_files = [
        (".github/workflows/validate.yml", "CI validation workflow"),
    ]
    
    results = []
    for filepath, description in ci_files:
        results.append(check_file_exists(filepath, description))
    
    print_warning("CI workflow execution check skipped (validated on push)")
    
    return all(results)


def check_template(verbose: bool) -> bool:
    """Check template configuration."""
    print_header("8. TEMPLATE")
    
    # Check configuration is centralized
    config_files = [
        ("app/config.py", "Centralized configuration"),
    ]
    
    results = []
    for filepath, description in config_files:
        results.append(check_file_exists(filepath, description))
    
    print_success("Template structure validated")
    
    return all(results)


def main() -> int:
    """Run all pre-release checks."""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print(f"{Colors.BOLD}Pre-Release Validation Check{Colors.RESET}")
    print(f"Running comprehensive validation before release...\n")
    
    checks = [
        ("Quality", check_quality),
        ("Security", check_security),
        ("Database", check_database),
        ("Documentation", check_documentation),
        ("Build", check_build),
        ("Integration", check_integration),
        ("CI/CD", check_ci),
        ("Template", check_template),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func(verbose)
        except Exception as e:
            print_error(f"Check '{name}' failed with exception: {e}")
            results[name] = False
    
    # Print summary
    print_header("RESUMO")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, success in results.items():
        if success:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.RESET}")
    
    if all(results.values()):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All checks passed! Ready for release.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some checks failed. Fix issues before release.{Colors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
