"""Guardrails de resposta para limites, tom e proibicoes."""

from dataclasses import dataclass
import re

DEFAULT_GUARDRAIL_FALLBACK_TEXT = (
    "Posso te ajudar com seguranca. Vou te encaminhar para um atendente humano continuar esse suporte."
)

_PROHIBITED_PATTERNS: tuple[tuple[str, re.Pattern[str], str], ...] = (
    (
        "secret_token",
        re.compile(r"\bsk-[a-zA-Z0-9]{16,}\b"),
        "Detectado possivel token sensivel na resposta.",
    ),
    (
        "credential_exposure",
        re.compile(r"\b(api\s*key|token\s*de\s*acesso|senha\s*interna)\b", flags=re.IGNORECASE),
        "Detectada referencia explicita a credencial sensivel.",
    ),
    (
        "abusive_language",
        re.compile(r"\b(idiota|burro|estupido|otario)\b", flags=re.IGNORECASE),
        "Detectada linguagem ofensiva para atendimento.",
    ),
)


@dataclass(frozen=True, slots=True)
class GuardrailViolation:
    """Representa violacao identificada durante avaliacao de resposta."""

    code: str
    detail: str


@dataclass(frozen=True, slots=True)
class GuardrailResult:
    """Resultado final da aplicacao de guardrails."""

    output_text: str
    blocked: bool
    transformed: bool
    violations: tuple[GuardrailViolation, ...]


def apply_response_guardrails(
    message: str,
    *,
    max_chars: int = 700,
    fallback_text: str = DEFAULT_GUARDRAIL_FALLBACK_TEXT,
) -> GuardrailResult:
    """Aplica guardrails de seguranca e tom em resposta textual do agente."""
    normalized_message = _normalize_whitespace(message)
    if not normalized_message:
        return _build_blocked_result(
            fallback_text=fallback_text,
            violation=GuardrailViolation(
                code="empty_response",
                detail="Resposta vazia apos normalizacao.",
            ),
        )

    prohibited_violations = _collect_prohibited_violations(normalized_message)
    if prohibited_violations:
        return GuardrailResult(
            output_text=fallback_text,
            blocked=True,
            transformed=True,
            violations=tuple(prohibited_violations),
        )

    working_text = normalized_message
    violations: list[GuardrailViolation] = []
    transformed = False

    toned_text, tone_changed = _normalize_tone(working_text)
    if tone_changed:
        transformed = True
        violations.append(
            GuardrailViolation(
                code="tone_adjusted",
                detail="Tom normalizado para padrao profissional e cordial.",
            )
        )
        working_text = toned_text

    if max_chars > 3 and len(working_text) > max_chars:
        transformed = True
        working_text = f"{working_text[: max_chars - 3].rstrip()}..."
        violations.append(
            GuardrailViolation(
                code="length_limited",
                detail=f"Resposta truncada para limite maximo de {max_chars} caracteres.",
            )
        )

    return GuardrailResult(
        output_text=working_text,
        blocked=False,
        transformed=transformed,
        violations=tuple(violations),
    )


def _build_blocked_result(*, fallback_text: str, violation: GuardrailViolation) -> GuardrailResult:
    return GuardrailResult(
        output_text=fallback_text,
        blocked=True,
        transformed=True,
        violations=(violation,),
    )


def _collect_prohibited_violations(message: str) -> list[GuardrailViolation]:
    violations: list[GuardrailViolation] = []
    for code, pattern, detail in _PROHIBITED_PATTERNS:
        if pattern.search(message):
            violations.append(GuardrailViolation(code=code, detail=detail))

    return violations


def _normalize_whitespace(message: str) -> str:
    return " ".join(message.split())


def _normalize_tone(message: str) -> tuple[str, bool]:
    toned_text = re.sub(r"([!?])\1+", r"\1", message)
    changed = toned_text != message

    uppercase_ratio = _compute_uppercase_ratio(toned_text)
    if uppercase_ratio >= 0.65:
        toned_text = toned_text.lower().capitalize()
        changed = True

    return toned_text, changed


def _compute_uppercase_ratio(message: str) -> float:
    letters = [char for char in message if char.isalpha()]
    if not letters:
        return 0.0

    uppercase_count = sum(1 for char in letters if char.isupper())
    return uppercase_count / len(letters)
