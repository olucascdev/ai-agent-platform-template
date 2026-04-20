"""Testes de logs estruturados com correlation id (fase 8.1)."""

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_whatsapp_webhook_pipeline_service
from app.main import CORRELATION_ID_HEADER, app
from app.preprocessing import normalize_incoming_event
from app.services import WebhookPipelineResult


class _FakeWebhookPipelineService:
    """Pipeline fake para evitar dependencias externas em teste de logging."""

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


def _extract_structured_logs(caplog) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for record in caplog.records:
        try:
            payload = json.loads(record.getMessage())
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict) and "event" in payload:
            events.append(payload)

    return events


def test_webhook_logs_include_required_observability_fields(caplog) -> None:
    """Garante logs estruturados com correlation id, evento e status HTTP."""
    caplog.set_level(logging.INFO, logger="app.observability")

    with _client_with_fake_pipeline() as client:
        response = client.post(
            "/webhook/whatsapp",
            headers={CORRELATION_ID_HEADER: "corr-fixed-123"},
            json={
                "eventId": "evt-obs-1",
                "sessionId": "sessao-obs",
                "contact": {"phonenumber": "+5531999999999"},
                "lastMessage": {"id": "msg-obs-1", "type": "TEXT", "text": "Ola"},
            },
        )

    assert response.status_code == 202
    assert response.headers[CORRELATION_ID_HEADER] == "corr-fixed-123"

    logs = _extract_structured_logs(caplog)
    completed_event = next(log for log in logs if log["event"] == "http_request_completed")
    accepted_event = next(log for log in logs if log["event"] == "webhook_whatsapp_accepted")

    assert completed_event["correlation_id"] == "corr-fixed-123"
    assert completed_event["method"] == "POST"
    assert completed_event["path"] == "/webhook/whatsapp"
    assert completed_event["status_code"] == 202
    assert "duration_ms" in completed_event

    assert accepted_event["correlation_id"] == "corr-fixed-123"
    assert accepted_event["event_id"] == "evt-obs-1"
    assert accepted_event["message_id"] == "msg-obs-1"


def test_health_request_generates_and_propagates_correlation_id(caplog) -> None:
    """Gera correlation id quando header nao e enviado e propaga no response."""
    caplog.set_level(logging.INFO, logger="app.observability")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    generated_correlation_id = response.headers[CORRELATION_ID_HEADER]
    assert generated_correlation_id

    logs = _extract_structured_logs(caplog)
    completed_event = next(log for log in logs if log["event"] == "http_request_completed")
    assert completed_event["correlation_id"] == generated_correlation_id
    assert completed_event["path"] == "/health"
    assert completed_event["status_code"] == 200
