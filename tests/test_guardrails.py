"""Testes de guardrails de resposta para limites, tom e proibicoes."""

from app.agent.guardrails import DEFAULT_GUARDRAIL_FALLBACK_TEXT, apply_response_guardrails


def test_apply_response_guardrails_blocks_empty_response() -> None:
    """Bloqueia resposta vazia e retorna fallback seguro."""
    result = apply_response_guardrails("   ")

    assert result.blocked is True
    assert result.output_text == DEFAULT_GUARDRAIL_FALLBACK_TEXT
    assert result.violations[0].code == "empty_response"


def test_apply_response_guardrails_blocks_secret_token_exposure() -> None:
    """Bloqueia resposta com padrao de token sensivel."""
    result = apply_response_guardrails("Use este token: sk-ABCD1234ABCD1234ABCD para acessar")

    assert result.blocked is True
    assert result.output_text == DEFAULT_GUARDRAIL_FALLBACK_TEXT
    assert any(violation.code == "secret_token" for violation in result.violations)


def test_apply_response_guardrails_adjusts_tone_when_text_is_aggressive() -> None:
    """Normaliza caixa alta excessiva e pontuacao repetida."""
    result = apply_response_guardrails("RESOLVA ISSO AGORA!!!")

    assert result.blocked is False
    assert result.transformed is True
    assert result.output_text == "Resolva isso agora!"
    assert any(violation.code == "tone_adjusted" for violation in result.violations)


def test_apply_response_guardrails_limits_maximum_length() -> None:
    """Trunca resposta longa para manter limite de envio."""
    result = apply_response_guardrails("a" * 60, max_chars=20)

    assert result.blocked is False
    assert result.output_text == "aaaaaaaaaaaaaaaaa..."
    assert any(violation.code == "length_limited" for violation in result.violations)


def test_apply_response_guardrails_keeps_safe_message_without_changes() -> None:
    """Mantem mensagem valida sem transformacoes desnecessarias."""
    result = apply_response_guardrails("Perfeito, vou te ajudar com os proximos passos.")

    assert result.blocked is False
    assert result.transformed is False
    assert result.output_text == "Perfeito, vou te ajudar com os proximos passos."
    assert result.violations == ()
