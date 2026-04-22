"""Construcao de contexto dinamico por mensagem para o agente."""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.preprocessing.event_normalizer import NormalizedIncomingEvent


def build_runtime_context_block(
    event: NormalizedIncomingEvent,
    *,
    customer_tier: str | None = None,
    lead_history: str | None = None,
    timezone_name: str = "America/Sao_Paulo",
) -> str:
    """Monta bloco XML-like com dados dinamicos do lead para o prompt por mensagem."""
    now = _resolve_now(timezone_name)
    formatted_time = now.strftime("%H:%M:%S")
    formatted_datetime = now.strftime("%d/%m/%y %H:%M")
    lead_name = _extract_first_name(event.contact_name)

    lines = [
        "<dadosLead>",
        f"  <nome>{_escape_tag_value(lead_name or '-')}</nome>",
        f"  <telefone>{_escape_tag_value(event.contact_phone)}</telefone>",
        f"  <horario_contato>{formatted_time}</horario_contato>",
        "  <contexto_lead>",
        f"    <historico_conversa>{_escape_tag_value(_normalize_optional(lead_history) or '-')}</historico_conversa>",
        f"    <categoria_cliente>{_escape_tag_value(_normalize_optional(customer_tier) or '-')}</categoria_cliente>",
        "  </contexto_lead>",
        "  <periodo_dia>",
        f"    -- horario atual: {formatted_datetime} --",
        "    <!-- 06:00-11:59 = Bom dia -->",
        "    <!-- 12:00-17:59 = Boa tarde -->",
        "    <!-- 18:00-05:59 = Boa noite -->",
        "  </periodo_dia>",
        f"  <session_id>{_escape_tag_value(event.session_id)}</session_id>",
        "</dadosLead>",
    ]
    return "\n".join(lines)


def compose_message_with_runtime_context(runtime_context_block: str, message_for_agent: str) -> str:
    """Concatena contexto dinamico e mensagem principal final enviada ao agente."""
    normalized_context = runtime_context_block.strip()
    normalized_message = message_for_agent.strip()
    if not normalized_context:
        return normalized_message
    if not normalized_message:
        return normalized_context

    return f"{normalized_context}\n\n{normalized_message}".strip()


def _resolve_now(timezone_name: str) -> datetime:
    normalized_timezone = _normalize_optional(timezone_name) or "America/Sao_Paulo"
    try:
        return datetime.now(ZoneInfo(normalized_timezone))
    except ZoneInfoNotFoundError:
        return datetime.now()


def _extract_first_name(full_name: str | None) -> str | None:
    normalized = _normalize_optional(full_name)
    if normalized is None:
        return None

    return normalized.split()[0]


def _escape_tag_value(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None
