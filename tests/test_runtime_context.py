"""Testes para contexto dinamico de runtime enviado ao agente."""

from app.agent.runtime_context import build_runtime_context_block, compose_message_with_runtime_context
from app.preprocessing.event_normalizer import NormalizedIncomingEvent


def _build_event() -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sess-123",
        contact_phone="+5511999999999",
        input_type="text",
        text="Quero ajuda",
        attachments=[],
        message_id="msg-1",
        message_created_at="2026-04-22T15:00:00Z",
        message_type_raw="TEXT",
        contact_name="Joel Silva",
        channel_platform="WhatsApp",
    )


def test_build_runtime_context_block_includes_expected_tags() -> None:
    """Monta bloco com dados essenciais para equivalencia de contexto com n8n."""
    block = build_runtime_context_block(
        _build_event(),
        customer_tier="diamante",
        lead_history="Lead sem resposta desde ontem",
    )

    assert "<dadosLead>" in block
    assert "<nome>Joel</nome>" in block
    assert "<telefone>+5511999999999</telefone>" in block
    assert "<session_id>sess-123</session_id>" in block
    assert "<categoria_cliente>diamante</categoria_cliente>" in block
    assert "<historico_conversa>Lead sem resposta desde ontem</historico_conversa>" in block


def test_compose_message_with_runtime_context_concatenates_blocks() -> None:
    """Concatena bloco de contexto com mensagem principal do agente."""
    result = compose_message_with_runtime_context("<dadosLead>...</dadosLead>", "[mensagem_principal]\nfonte=text\nOi")

    assert result.startswith("<dadosLead>...")
    assert "[mensagem_principal]" in result
