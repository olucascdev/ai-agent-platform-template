"""Testes das regras de FAQ, qualificacao e transferencia por departamento."""

import pytest

from app.agent.conversation_rules import evaluate_conversation_rules


def test_evaluate_conversation_rules_matches_faq_and_keeps_flow_without_transfer() -> None:
    """Confirma deteccao de FAQ sem acionar handoff de departamento."""
    decision = evaluate_conversation_rules("Qual o horario de atendimento?")

    assert decision.intent == "faq"
    assert decision.faq is not None
    assert decision.faq.key == "business_hours"
    assert "horario de atendimento" in decision.faq.answer.lower()
    assert decision.transfer.should_transfer is False


def test_evaluate_conversation_rules_tracks_qualification_gaps() -> None:
    """Valida qualificacao parcial quando faltam sinais de prazo."""
    decision = evaluate_conversation_rules("Quero contratar e tenho orcamento de 2 mil reais")

    assert decision.intent == "qualification"
    assert decision.qualification.has_goal is True
    assert decision.qualification.has_budget_signal is True
    assert decision.qualification.has_timeline_signal is False
    assert decision.qualification.is_ready_for_handoff is False
    assert decision.qualification.missing_fields == ("timeline",)
    assert decision.qualification.next_question is not None
    assert decision.transfer.should_transfer is False


def test_evaluate_conversation_rules_routes_human_request_to_department() -> None:
    """Garante transferencia imediata quando cliente pede humano explicitamente."""
    decision = evaluate_conversation_rules(
        "Quero falar com um atendente humano agora",
        department_ids={"human_handoff": "dep-human"},
    )

    assert decision.intent == "transfer"
    assert decision.transfer.should_transfer is True
    assert decision.transfer.department_key == "human_handoff"
    assert decision.transfer.department_id == "dep-human"


def test_evaluate_conversation_rules_routes_qualified_lead_to_sales() -> None:
    """Valida transferencia comercial quando lead apresenta sinais de qualificacao completa."""
    decision = evaluate_conversation_rules(
        "Quero contratar hoje e posso investir 3000 por mes",
        department_ids={"sales": "dep-sales"},
    )

    assert decision.intent == "transfer"
    assert decision.qualification.is_ready_for_handoff is True
    assert decision.transfer.should_transfer is True
    assert decision.transfer.department_key == "sales"
    assert decision.transfer.department_id == "dep-sales"


def test_evaluate_conversation_rules_routes_support_issue_to_support_department() -> None:
    """Confirma roteamento para suporte quando mensagem indica erro/problema tecnico."""
    decision = evaluate_conversation_rules(
        "Meu acesso nao funciona, estou com erro no login",
        department_ids={"support": "dep-support"},
    )

    assert decision.intent == "transfer"
    assert decision.transfer.department_key == "support"
    assert decision.transfer.department_id == "dep-support"


@pytest.mark.parametrize("message", ["", "   "])
def test_evaluate_conversation_rules_raises_for_blank_message(message: str) -> None:
    """Garante erro explicito para entrada textual vazia."""
    with pytest.raises(ValueError) as exc_info:
        evaluate_conversation_rules(message)

    assert "message deve ser informado" in str(exc_info.value)
