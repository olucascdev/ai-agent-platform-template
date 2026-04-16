"""Testes de composicao de sessao single-client do agente."""

import pytest

from app.agent.session import build_single_client_session_id


def test_build_single_client_session_id_uses_explicit_prefix_and_normalizes_phone() -> None:
    """Garante formatacao `prefixo:telefone` com telefone normalizado em digitos."""
    session_id = build_single_client_session_id(
        "+55 (11) 99999-1234",
        session_prefix="spacecont",
    )

    assert session_id == "spacecont:5511999991234"


def test_build_single_client_session_id_uses_default_prefix_from_settings() -> None:
    """Confirma fallback para `AGENT_SESSION_PREFIX` quando prefixo nao e informado."""
    session_id = build_single_client_session_id("5511888887777")

    assert session_id == "spacecont:5511888887777"


@pytest.mark.parametrize(
    ("contact_phone", "expected_message"),
    [
        ("", "contact_phone deve ser informado"),
        ("   ", "contact_phone deve ser informado"),
        ("( ) -", "contact_phone deve conter ao menos um digito"),
    ],
)
def test_build_single_client_session_id_raises_for_invalid_phone(contact_phone: str, expected_message: str) -> None:
    """Valida erro explicito para telefone vazio ou sem digitos."""
    with pytest.raises(ValueError) as exc_info:
        build_single_client_session_id(contact_phone, session_prefix="spacecont")

    assert expected_message in str(exc_info.value)


def test_build_single_client_session_id_raises_for_blank_prefix() -> None:
    """Valida erro explicito quando prefixo e branco."""
    with pytest.raises(ValueError) as exc_info:
        build_single_client_session_id("5511999999999", session_prefix="   ")

    assert "session_prefix deve ser informado" in str(exc_info.value)
