"""Testes do endpoint `POST /webhook/whatsapp` da fase 7.1."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_whatsapp_webhook_pipeline_service
from app.main import app
from app.preprocessing import normalize_incoming_event
from app.services import WebhookPipelineResult


class _FakeWebhookPipelineService:
    """Pipeline fake para evitar dependencias externas nos testes de rota."""

    async def process(self, raw_payload: dict[str, Any]) -> WebhookPipelineResult:
        normalized_event = normalize_incoming_event(raw_payload)
        return WebhookPipelineResult(
            normalized_event=normalized_event,
            event_id=raw_payload.get("eventId"),
            idempotency_key=None,
            is_duplicate=False,
            session_command=None,
            lead_status="message_sent",
            lead_id=1,
            crm_contact_id="contact-1",
            agent_response_text="Resposta teste",
            sent_message_text="Resposta teste",
            sender_status_code=200,
            sender_payload={"queued": True},
        )


@contextmanager
def _client_with_fake_pipeline() -> Iterator[TestClient]:
    app.dependency_overrides[get_whatsapp_webhook_pipeline_service] = _FakeWebhookPipelineService
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def test_webhook_whatsapp_accepts_wrapped_payload() -> None:
    """Aceita payload com wrapper `body` e retorna resumo validado do evento."""
    with _client_with_fake_pipeline() as client:
        payload = {
            "body": {
                "eventId": "evt-900",
                "sessionId": "sessao-123",
                "contact": {"phonenumber": "+5531999999999", "name": "Joel"},
                "lastMessage": {
                    "id": "msg-1",
                    "createdAt": "2026-04-20T10:00:00Z",
                    "type": "TEXT",
                    "text": "Oi",
                },
            }
        }

        response = client.post("/webhook/whatsapp", json=payload)

        assert response.status_code == 202
        assert response.json() == {
            "status": "accepted",
            "session_id": "sessao-123",
            "contact_phone": "+5531999999999",
            "message_id": "msg-1",
            "event_id": "evt-900",
            "is_duplicate": False,
            "session_command": None,
        }


def test_webhook_whatsapp_accepts_direct_payload_without_wrapper() -> None:
    """Aceita payload direto sem `body`, mantendo compatibilidade com emissores simples."""
    with _client_with_fake_pipeline() as client:
        payload = {
            "session": {"id": "sessao-456"},
            "contact": {"phone": "+5531888888888"},
            "lastMessage": {"id": "msg-2", "type": "TEXT", "text": "Teste"},
        }

        response = client.post("/webhook/whatsapp", json=payload)

        assert response.status_code == 202
        assert response.json()["status"] == "accepted"
        assert response.json()["session_id"] == "sessao-456"
        assert response.json()["contact_phone"] == "+5531888888888"
        assert response.json()["message_id"] == "msg-2"
        assert response.json()["event_id"] is None
        assert response.json()["is_duplicate"] is False
        assert response.json()["session_command"] is None


def test_webhook_whatsapp_rejects_payload_with_invalid_wrapper_type() -> None:
    """Retorna 422 quando `body` nao e um objeto valido de evento."""
    with _client_with_fake_pipeline() as client:
        response = client.post("/webhook/whatsapp", json={"body": "invalid"})

        assert response.status_code == 422


def test_webhook_whatsapp_rejects_payload_without_session_id() -> None:
    """Retorna 422 quando nem `sessionId` nem `session.id` sao informados."""
    with _client_with_fake_pipeline() as client:
        payload = {
            "contact": {"phonenumber": "+5531777777777"},
            "lastMessage": {"id": "msg-3", "type": "TEXT", "text": "Oi"},
        }
        response = client.post("/webhook/whatsapp", json=payload)

        assert response.status_code == 422
        assert "session_id" in response.text


def test_webhook_whatsapp_rejects_payload_without_contact_phone() -> None:
    """Retorna 422 quando bloco de contato nao traz nenhum telefone valido."""
    with _client_with_fake_pipeline() as client:
        payload = {
            "sessionId": "sessao-999",
            "contact": {"name": "Sem Telefone"},
            "lastMessage": {"id": "msg-9", "type": "TEXT", "text": "Oi"},
        }
        response = client.post("/webhook/whatsapp", json=payload)

        assert response.status_code == 422
        assert "contact_phone" in response.text


def test_webhook_whatsapp_marks_duplicate_when_pipeline_short_circuits() -> None:
    """Retorna `is_duplicate=true` quando pipeline identifica evento repetido."""

    class _FakeDuplicatePipelineService:
        async def process(self, raw_payload: dict[str, Any]) -> WebhookPipelineResult:
            normalized_event = normalize_incoming_event(raw_payload)
            return WebhookPipelineResult(
                normalized_event=normalized_event,
                event_id=raw_payload.get("eventId"),
                idempotency_key="event:evt-dup",
                is_duplicate=True,
                session_command=None,
                lead_status="duplicate_ignored",
                lead_id=None,
                crm_contact_id=None,
                agent_response_text="",
                sent_message_text="",
                sender_status_code=None,
                sender_payload=None,
            )

    app.dependency_overrides[get_whatsapp_webhook_pipeline_service] = _FakeDuplicatePipelineService
    client = TestClient(app)
    try:
        response = client.post(
            "/webhook/whatsapp",
            json={
                "eventId": "evt-dup",
                "sessionId": "sessao-dup",
                "contact": {"phonenumber": "+5531666666666"},
                "lastMessage": {"id": "msg-dup", "type": "TEXT", "text": "Oi"},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["is_duplicate"] is True
    assert response.json()["session_command"] is None


def test_webhook_whatsapp_exposes_session_command_when_reset_is_processed() -> None:
    """Retorna comando de sessao processado para observabilidade do fluxo."""

    class _FakeResetPipelineService:
        async def process(self, raw_payload: dict[str, Any]) -> WebhookPipelineResult:
            normalized_event = normalize_incoming_event(raw_payload)
            return WebhookPipelineResult(
                normalized_event=normalized_event,
                event_id=raw_payload.get("eventId"),
                idempotency_key="event:evt-reset",
                is_duplicate=False,
                session_command="reset",
                lead_status="session_reset",
                lead_id=1,
                crm_contact_id=None,
                agent_response_text="",
                sent_message_text="Sessao reiniciada com sucesso.",
                sender_status_code=200,
                sender_payload={"queued": True},
            )

    app.dependency_overrides[get_whatsapp_webhook_pipeline_service] = _FakeResetPipelineService
    client = TestClient(app)
    try:
        response = client.post(
            "/webhook/whatsapp",
            json={
                "eventId": "evt-reset",
                "sessionId": "sessao-1",
                "contact": {"phonenumber": "+5531111111111"},
                "lastMessage": {"id": "msg-reset", "type": "TEXT", "text": "/reset"},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["session_command"] == "reset"
