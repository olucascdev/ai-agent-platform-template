"""Tratamento de comandos de sessao recebidos via webhook."""

import unicodedata
from typing import Literal

SessionCommand = Literal["reset"]

_RESET_ALIASES = {"reset", "/reset", "restart", "/restart", "reiniciar", "/reiniciar"}

SESSION_RESET_CONFIRMATION_TEXT = "Sessao reiniciada com sucesso. Podemos comecar de novo quando voce quiser."


def resolve_session_command(message_text: str | None) -> SessionCommand | None:
    """Identifica comando de sessao no texto recebido, quando existir."""
    normalized = _normalize_command_text(message_text)
    if not normalized:
        return None

    if normalized in _RESET_ALIASES:
        return "reset"

    return None


def build_session_command_reply(command: SessionCommand) -> str:
    """Retorna resposta padrao para comando de sessao reconhecido."""
    if command == "reset":
        return SESSION_RESET_CONFIRMATION_TEXT

    return "Comando de sessao processado."


def _normalize_command_text(value: str | None) -> str:
    if value is None:
        return ""

    compact = " ".join(value.strip().lower().split())
    if not compact:
        return ""

    normalized = unicodedata.normalize("NFKD", compact)
    return "".join(char for char in normalized if not unicodedata.combining(char))
