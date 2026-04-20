"""Politica de segredos para bloquear hardcodes em codigo e workflows."""

from dataclasses import dataclass
from pathlib import Path
import re

KNOWN_SECRET_ENV_NAMES: tuple[str, ...] = (
    "OPENAI_API_KEY",
    "GOOGLE_API_KEY",
    "AGENT_MODEL_API_KEY",
    "OPENROUTER_API_KEY",
    "GROQ_API_KEY",
    "ANTHROPIC_API_KEY",
    "CRM_TOKEN",
    "WHATSAPP_TOKEN",
    "DATABASE_URL",
    "DATABASE_URL_MIGRATIONS",
)

_REAL_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "openai_like_key",
        re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    ),
    (
        "github_pat",
        re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "google_api_key",
        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    ),
)

_WORKFLOW_SECRET_LINE = re.compile(r"^\s*([A-Z0-9_]+)\s*:\s*(.+?)\s*$")
_CODE_ASSIGNMENT_TEMPLATE = r"\b{env_name}\b\s*=\s*([\"'])(.*?)\1"
_SCRIPT_EXPORT_TEMPLATE = r"\bexport\s+{env_name}\s*=\s*([\"'])(.*?)\1"
_SAFE_NON_SECRET_PLACEHOLDERS = {
    "postgresql+asyncpg://ai:ai@localhost:5432/ai",
    "postgresql://ai:ai@localhost:5432/ai",
}


@dataclass(frozen=True, slots=True)
class SecretPolicyViolation:
    """Violacao encontrada durante varredura de politica de segredos."""

    file_path: str
    line_number: int
    rule: str
    message: str
    snippet: str


def scan_repository_for_secret_policy_violations(repo_root: Path) -> list[SecretPolicyViolation]:
    """Varre codigo e workflows em busca de hardcode de segredo."""
    targets = [
        repo_root / "app",
        repo_root / "db",
        repo_root / ".github" / "workflows",
        repo_root / "scripts",
    ]

    violations: list[SecretPolicyViolation] = []
    for target in targets:
        if not target.exists():
            continue

        for file_path in _iter_target_files(target):
            relative_path = file_path.relative_to(repo_root)
            content = file_path.read_text(encoding="utf-8")
            violations.extend(scan_text_for_secret_policy_violations(relative_path, content))

    return violations


def scan_text_for_secret_policy_violations(file_path: Path, text: str) -> list[SecretPolicyViolation]:
    """Aplica regras de politica de segredos em texto de arquivo unico."""
    suffix = file_path.suffix.lower()
    normalized_path = file_path.as_posix()

    violations: list[SecretPolicyViolation] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue

        if suffix in {".yml", ".yaml"}:
            workflow_match = _WORKFLOW_SECRET_LINE.match(line)
            if workflow_match is not None:
                env_name = workflow_match.group(1)
                value = workflow_match.group(2).strip()
                if env_name in KNOWN_SECRET_ENV_NAMES and _is_literal_secret_value(value):
                    violations.append(
                        SecretPolicyViolation(
                            file_path=normalized_path,
                            line_number=line_number,
                            rule="workflow_secret_literal",
                            message=f"Workflow define segredo `{env_name}` com valor literal.",
                            snippet=stripped,
                        )
                    )

        if suffix in {".py", ".sh"}:
            for env_name in KNOWN_SECRET_ENV_NAMES:
                assignment_pattern = re.compile(_CODE_ASSIGNMENT_TEMPLATE.format(env_name=re.escape(env_name)))
                script_export_pattern = re.compile(_SCRIPT_EXPORT_TEMPLATE.format(env_name=re.escape(env_name)))
                assignment_match = assignment_pattern.search(line)
                export_match = script_export_pattern.search(line)
                match = assignment_match or export_match
                if match is None:
                    continue

                assigned_value = match.group(2).strip()
                if assigned_value:
                    violations.append(
                        SecretPolicyViolation(
                            file_path=normalized_path,
                            line_number=line_number,
                            rule="code_secret_literal",
                            message=f"Codigo define segredo `{env_name}` com valor literal.",
                            snippet=stripped,
                        )
                    )

        for rule, pattern in _REAL_SECRET_PATTERNS:
            if pattern.search(line):
                violations.append(
                    SecretPolicyViolation(
                        file_path=normalized_path,
                        line_number=line_number,
                        rule=rule,
                        message="Possivel segredo real detectado por padrao de token.",
                        snippet=stripped,
                    )
                )

    return violations


def _iter_target_files(target: Path) -> list[Path]:
    if target.name == "workflows":
        return sorted(
            [
                *target.glob("*.yml"),
                *target.glob("*.yaml"),
            ]
        )

    if target.name == "scripts":
        return sorted(target.glob("*.sh"))

    return sorted(target.rglob("*.py"))


def _is_literal_secret_value(value: str) -> bool:
    stripped = value.strip()
    if not stripped:
        return False

    if "${{" in stripped:
        return False

    if (stripped.startswith('"') and stripped.endswith('"')) or (stripped.startswith("'") and stripped.endswith("'")):
        stripped = stripped[1:-1].strip()

    if not stripped:
        return False

    if _is_safe_placeholder_value(stripped):
        return False

    return True


def _is_safe_placeholder_value(value: str) -> bool:
    if value in _SAFE_NON_SECRET_PLACEHOLDERS:
        return True

    if value.startswith("postgresql") and "://ai:ai@localhost:" in value:
        return True

    return False
