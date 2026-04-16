"""Helpers para composicao de sessao single-client do agente."""

import re

from app.config import settings

_NON_DIGIT_PATTERN = re.compile(r"\D+")


def build_single_client_session_id(contact_phone: str, *, session_prefix: str | None = None) -> str:
    """Monta `session_id` no formato `prefixo:telefone` para isolamento por cliente."""
    resolved_prefix = (session_prefix if session_prefix is not None else settings.agent_session_prefix).strip()
    if not resolved_prefix:
        raise ValueError("session_prefix deve ser informado para compor session_id single-client.")

    normalized_phone = _normalize_contact_phone(contact_phone)
    return f"{resolved_prefix}:{normalized_phone}"


def _normalize_contact_phone(contact_phone: str) -> str:
    phone = contact_phone.strip()
    if not phone:
        raise ValueError("contact_phone deve ser informado para compor session_id.")

    digits_only = _NON_DIGIT_PATTERN.sub("", phone)
    if not digits_only:
        raise ValueError("contact_phone deve conter ao menos um digito para compor session_id.")

    return digits_only
