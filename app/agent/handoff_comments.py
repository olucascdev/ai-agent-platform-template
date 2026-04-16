"""Geracao de comments estruturados para handoff humano no CRM."""

from dataclasses import dataclass

from app.agent.conversation_rules import ConversationRulesDecision


@dataclass(frozen=True, slots=True)
class HandoffCommentInput:
    """Dados necessarios para gerar comment estruturado de transferencia."""

    contact_phone: str
    decision: ConversationRulesDecision
    contact_name: str | None = None
    session_id: str | None = None
    latest_user_message: str | None = None


def build_structured_handoff_comment(
    payload: HandoffCommentInput,
    *,
    max_message_chars: int = 240,
) -> str:
    """Monta comments em formato estruturado para handoff humano no CRM."""
    if not payload.decision.transfer.should_transfer:
        raise ValueError("Nao e possivel gerar handoff comment sem decisao de transferencia ativa.")

    normalized_phone = _normalize_required_field(payload.contact_phone, field_name="contact_phone")
    message_preview = _normalize_optional_text(payload.latest_user_message, max_chars=max_message_chars)
    transfer_reason = _normalize_optional_text(payload.decision.transfer.reason, max_chars=180)

    missing_fields = payload.decision.qualification.missing_fields
    if missing_fields:
        qualification_missing = ",".join(missing_fields)
    else:
        qualification_missing = "none"

    lines = [
        "[handoff_v1]",
        f"intent={payload.decision.intent}",
        f"department_key={_normalize_optional_text(payload.decision.transfer.department_key)}",
        f"department_id={_normalize_optional_text(payload.decision.transfer.department_id)}",
        f"reason={transfer_reason}",
        f"contact_phone={normalized_phone}",
        f"contact_name={_normalize_optional_text(payload.contact_name)}",
        f"session_id={_normalize_optional_text(payload.session_id)}",
        f"qualification_ready={_bool_as_flag(payload.decision.qualification.is_ready_for_handoff)}",
        f"qualification_missing={qualification_missing}",
        f"faq_key={_normalize_optional_text(payload.decision.faq.key if payload.decision.faq else None)}",
        f"latest_user_message={message_preview}",
    ]
    return "\n".join(lines).strip()


def _normalize_required_field(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} deve ser informado para gerar handoff comment.")

    return normalized


def _normalize_optional_text(value: str | None, *, max_chars: int | None = None) -> str:
    if value is None:
        return "-"

    normalized = " ".join(value.split())
    if not normalized:
        return "-"

    if max_chars is not None and max_chars > 3 and len(normalized) > max_chars:
        return f"{normalized[: max_chars - 3].rstrip()}..."

    return normalized


def _bool_as_flag(value: bool) -> str:
    return "yes" if value else "no"
