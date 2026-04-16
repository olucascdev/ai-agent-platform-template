"""Testes de integracao simulada para fechamento de contratos HTTP da fase 4.5."""

import json
from typing import Any

import httpx
import pytest

from app.config import settings
from app.integrations import build_crm_client, build_whatsapp_sender_client
from app.integrations.http_client import HttpClientResponseError


def _json_body_from_request(request: httpx.Request) -> dict[str, Any]:
    if not request.content:
        return {}

    return json.loads(request.content.decode("utf-8"))


@pytest.mark.asyncio
async def test_simulated_flow_crm_lookup_transfer_and_sender_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Executa fluxo completo simulado validando contrato HTTP ponta a ponta."""
    received_requests: list[dict[str, Any]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        received_requests.append(
            {
                "host": request.url.host,
                "path": request.url.path,
                "method": request.method,
                "query": dict(request.url.params),
                "headers": dict(request.headers),
                "body": _json_body_from_request(request),
            }
        )

        if request.url.host == "crm.example.com" and request.url.path == "/api/v1/contacts":
            return httpx.Response(status_code=200, request=request, json={"data": [{"id": "contact-101"}]})

        if request.url.host == "crm.example.com" and request.url.path == "/api/v1/contacts/contact-101/ticket/transfer":
            return httpx.Response(status_code=200, request=request, json={"status": "transferred"})

        if request.url.host == "sender.example.com" and request.url.path == "/send/text":
            return httpx.Response(status_code=200, request=request, json={"messageId": "msg-555", "queued": True})

        return httpx.Response(status_code=404, request=request, json={"error": "route not mocked"})

    monkeypatch.setattr(settings, "crm_base_url", "https://crm.example.com/api/v1")
    monkeypatch.setattr(settings, "crm_token", "crm-token")
    monkeypatch.setattr(settings, "crm_contacts_lookup_path", "/contacts")
    monkeypatch.setattr(settings, "crm_lookup_phone_param", "where[data.number][$iLike]")
    monkeypatch.setattr(settings, "crm_lookup_phone_value_template", "%{phone}%")
    monkeypatch.setattr(settings, "crm_lookup_service_id_param", "where[serviceId]")
    monkeypatch.setattr(settings, "crm_service_id", "svc-01")
    monkeypatch.setattr(settings, "crm_transfer_path_template", "/contacts/{contact_id}/ticket/transfer")
    monkeypatch.setattr(settings, "crm_auth_header_name", "Authorization")
    monkeypatch.setattr(settings, "crm_auth_header_prefix", "Bearer")

    monkeypatch.setattr(settings, "whatsapp_sender_url", "https://sender.example.com/send/text")
    monkeypatch.setattr(settings, "whatsapp_token", "sender-token")
    monkeypatch.setattr(settings, "whatsapp_sender_method", "POST")
    monkeypatch.setattr(settings, "whatsapp_sender_number_field", "number")
    monkeypatch.setattr(settings, "whatsapp_sender_text_field", "text")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_name", "token")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_prefix", "")

    monkeypatch.setattr(settings, "http_timeout_seconds", 5.0)
    monkeypatch.setattr(settings, "http_max_retries", 1)
    monkeypatch.setattr(settings, "http_retry_backoff_seconds", 0.0)

    transport = httpx.MockTransport(handler)
    crm_client = build_crm_client(transport=transport)
    sender_client = build_whatsapp_sender_client(transport=transport)

    contact = await crm_client.find_contact_by_phone("+5531999999999")
    assert contact is not None
    assert contact.contact_id == "contact-101"

    transfer_response = await crm_client.transfer_contact(
        contact_id=contact.contact_id,
        department_id="dep-77",
        comments="Lead qualificado e pronto para atendimento humano.",
    )
    assert transfer_response == {"status": "transferred"}

    send_result = await sender_client.send_text(phone="+5531999999999", text="Ola! Recebemos sua solicitacao.")
    assert send_result.payload == {"messageId": "msg-555", "queued": True}

    assert len(received_requests) == 3

    lookup_request = received_requests[0]
    assert lookup_request["host"] == "crm.example.com"
    assert lookup_request["path"] == "/api/v1/contacts"
    assert lookup_request["method"] == "GET"
    assert lookup_request["query"]["where[data.number][$iLike]"] == "%+5531999999999%"
    assert lookup_request["query"]["where[serviceId]"] == "svc-01"
    assert lookup_request["headers"]["authorization"] == "Bearer crm-token"

    transfer_request = received_requests[1]
    assert transfer_request["host"] == "crm.example.com"
    assert transfer_request["path"] == "/api/v1/contacts/contact-101/ticket/transfer"
    assert transfer_request["method"] == "POST"
    assert transfer_request["body"] == {
        "departmentId": "dep-77",
        "comments": "Lead qualificado e pronto para atendimento humano.",
    }

    send_request = received_requests[2]
    assert send_request["host"] == "sender.example.com"
    assert send_request["path"] == "/send/text"
    assert send_request["method"] == "POST"
    assert send_request["headers"]["token"] == "sender-token"
    assert send_request["body"] == {
        "number": "+5531999999999",
        "text": "Ola! Recebemos sua solicitacao.",
    }


@pytest.mark.asyncio
async def test_simulated_retry_policy_differs_between_crm_and_sender(monkeypatch: pytest.MonkeyPatch) -> None:
    """Confirma que CRM e sender aplicam contratos de retry diferentes."""
    crm_attempts = 0
    sender_attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal crm_attempts, sender_attempts

        if request.url.host == "crm.example.com" and request.url.path == "/api/v1/contacts":
            crm_attempts += 1
            return httpx.Response(status_code=409, request=request, json={"error": "conflict"})

        if request.url.host == "sender.example.com" and request.url.path == "/send/text":
            sender_attempts += 1
            if sender_attempts == 1:
                return httpx.Response(status_code=425, request=request, json={"error": "too early"})

            return httpx.Response(status_code=200, request=request, json={"ok": True})

        return httpx.Response(status_code=404, request=request)

    monkeypatch.setattr(settings, "crm_base_url", "https://crm.example.com/api/v1")
    monkeypatch.setattr(settings, "crm_token", "crm-token")
    monkeypatch.setattr(settings, "crm_contacts_lookup_path", "/contacts")
    monkeypatch.setattr(settings, "crm_lookup_phone_param", "phone")
    monkeypatch.setattr(settings, "crm_lookup_phone_value_template", "{phone}")
    monkeypatch.setattr(settings, "crm_lookup_service_id_param", "serviceId")
    monkeypatch.setattr(settings, "crm_service_id", None)
    monkeypatch.setattr(settings, "crm_transfer_path_template", "/contacts/{contact_id}/ticket/transfer")
    monkeypatch.setattr(settings, "crm_auth_header_name", "Authorization")
    monkeypatch.setattr(settings, "crm_auth_header_prefix", "Bearer")

    monkeypatch.setattr(settings, "whatsapp_sender_url", "https://sender.example.com/send/text")
    monkeypatch.setattr(settings, "whatsapp_token", "sender-token")
    monkeypatch.setattr(settings, "whatsapp_sender_method", "POST")
    monkeypatch.setattr(settings, "whatsapp_sender_number_field", "number")
    monkeypatch.setattr(settings, "whatsapp_sender_text_field", "text")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_name", "Authorization")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_prefix", "Bearer")

    monkeypatch.setattr(settings, "http_timeout_seconds", 5.0)
    monkeypatch.setattr(settings, "http_max_retries", 1)
    monkeypatch.setattr(settings, "http_retry_backoff_seconds", 0.0)

    transport = httpx.MockTransport(handler)
    crm_client = build_crm_client(transport=transport)
    sender_client = build_whatsapp_sender_client(transport=transport)

    with pytest.raises(HttpClientResponseError) as crm_exc:
        await crm_client.find_contact_by_phone("+5531888888888")

    assert crm_attempts == 1
    assert crm_exc.value.status_code == 409
    assert crm_exc.value.retryable is False

    sender_result = await sender_client.send_text(phone="+5531888888888", text="Mensagem teste")
    assert sender_attempts == 2
    assert sender_result.payload == {"ok": True}
