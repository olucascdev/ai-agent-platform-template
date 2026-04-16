"""Testes de comments estruturados para handoff humano."""

import pytest

from app.agent.conversation_rules import evaluate_conversation_rules
from app.agent.handoff_comments import HandoffCommentInput, build_structured_handoff_comment


def test_build_structured_handoff_comment_generates_expected_contract() -> None:
    """Valida contrato textual estruturado usado no campo `comments` do CRM."""
    decision = evaluate_conversation_rules(
        "Quero falar com atendente humano",
        department_ids={"human_handoff": "dep-human"},
    )
    payload = HandoffCommentInput(
        contact_phone="+5511999999999",
        contact_name="Ana",
        session_id="spacecont:5511999999999",
        latest_user_message="Quero falar com atendente humano para resolver agora",
        decision=decision,
    )

    comment = build_structured_handoff_comment(payload, max_message_chars=30)

    assert "[handoff_v1]" in comment
    assert "intent=transfer" in comment
    assert "department_key=human_handoff" in comment
    assert "department_id=dep-human" in comment
    assert "contact_phone=+5511999999999" in comment
    assert "contact_name=Ana" in comment
    assert "session_id=spacecont:5511999999999" in comment
    assert "qualification_ready=no" in comment
    assert "qualification_missing=goal,budget,timeline" in comment
    assert "latest_user_message=Quero falar com atendente h..." in comment


def test_build_structured_handoff_comment_marks_no_missing_fields_when_qualified() -> None:
    """Confirma `qualification_missing=none` para lead totalmente qualificado."""
    decision = evaluate_conversation_rules(
        "Quero contratar hoje e posso investir 2000 por mes",
        department_ids={"sales": "dep-sales"},
    )
    payload = HandoffCommentInput(contact_phone="5511888887777", decision=decision)

    comment = build_structured_handoff_comment(payload)

    assert "department_key=sales" in comment
    assert "department_id=dep-sales" in comment
    assert "qualification_ready=yes" in comment
    assert "qualification_missing=none" in comment


def test_build_structured_handoff_comment_raises_when_transfer_is_not_active() -> None:
    """Garante erro explicito quando nao existe decisao de transferencia."""
    decision = evaluate_conversation_rules("Qual o horario de atendimento?")
    payload = HandoffCommentInput(contact_phone="5511999999999", decision=decision)

    with pytest.raises(ValueError) as exc_info:
        build_structured_handoff_comment(payload)

    assert "decisao de transferencia" in str(exc_info.value)
