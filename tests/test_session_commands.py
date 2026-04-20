"""Testes para resolucao de comandos de sessao do webhook."""

from app.services.session_commands import (
    SESSION_RESET_CONFIRMATION_TEXT,
    build_session_command_reply,
    resolve_session_command,
)


def test_resolve_session_command_accepts_reset_aliases() -> None:
    """Reconhece variacoes de comando reset com/sem barra e acento."""
    assert resolve_session_command("/reset") == "reset"
    assert resolve_session_command(" Reiniciar ") == "reset"
    assert resolve_session_command("RESTART") == "reset"


def test_resolve_session_command_returns_none_for_regular_messages() -> None:
    """Nao interpreta mensagem comum como comando de sessao."""
    assert resolve_session_command("quero saber o preco") is None
    assert resolve_session_command(None) is None


def test_build_session_command_reply_returns_reset_confirmation() -> None:
    """Garante resposta padrao para comando reset."""
    assert build_session_command_reply("reset") == SESSION_RESET_CONFIRMATION_TEXT
