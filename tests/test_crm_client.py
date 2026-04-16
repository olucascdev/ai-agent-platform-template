"""Testes do cliente de CRM configuravel da fase 4.2."""

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.config import settings
from app.integrations.contracts import IntegrationContractError
from app.integrations.crm_client import CRMClient, build_crm_client
from app.integrations.http_client import ResilientHttpClient


def _build_http_client(handler: Callable[[httpx.Request], httpx.Response]) -> ResilientHttpClient:
    return ResilientHttpClient(
        base_url="https://crm.example.com/api/v1",
        default_headers={"Authorization": "Bearer test-token"},
        timeout_seconds=10,
        max_retries=0,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_find_contact_by_phone_uses_configured_query_params() -> None:
    """Valida lookup com parametros customizados para diferentes CRMs."""
    seen_request: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_request["path"] = request.url.path
        seen_request["query"] = dict(request.url.params)
        seen_request["auth"] = request.headers.get("Authorization")
        return httpx.Response(status_code=200, request=request, json={"data": [{"id": "c-123", "name": "Ana"}]})

    client = CRMClient(
        http_client=_build_http_client(handler),
        contacts_lookup_path="/contacts",
        lookup_phone_param="where[data.number][$iLike]",
        lookup_phone_value_template="%{phone}%",
        lookup_service_id_param="where[serviceId]",
        service_id="svc-123",
    )

    contact = await client.find_contact_by_phone("+5531999999999")

    assert contact is not None
    assert contact.contact_id == "c-123"
    assert seen_request["path"] == "/api/v1/contacts"
    assert seen_request["query"]["where[data.number][$iLike]"] == "%+5531999999999%"
    assert seen_request["query"]["where[serviceId]"] == "svc-123"
    assert seen_request["auth"] == "Bearer test-token"


@pytest.mark.asyncio
async def test_find_contact_by_phone_returns_none_when_no_contact_found() -> None:
    """Retorna `None` quando o CRM nao devolve contato."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"data": []})

    client = CRMClient(http_client=_build_http_client(handler))

    contact = await client.find_contact_by_phone("+5531888888888")

    assert contact is None


@pytest.mark.asyncio
async def test_find_contact_by_phone_supports_single_object_payload() -> None:
    """Aceita payload com contato em objeto unico, sem lista `data`."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"id": "c-999", "name": "Bruna"})

    client = CRMClient(http_client=_build_http_client(handler))

    contact = await client.find_contact_by_phone("+5531777777777")

    assert contact is not None
    assert contact.contact_id == "c-999"
    assert contact.raw["name"] == "Bruna"


@pytest.mark.asyncio
async def test_transfer_contact_sends_expected_payload_and_path() -> None:
    """Valida payload de transferencia para departamento no CRM."""
    seen_request: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_request["path"] = request.url.path
        seen_request["method"] = request.method
        seen_request["body"] = request.content.decode("utf-8")
        return httpx.Response(status_code=200, request=request, json={"status": "queued"})

    client = CRMClient(
        http_client=_build_http_client(handler),
        transfer_path_template="/contacts/{contact_id}/ticket/transfer",
    )

    response_payload = await client.transfer_contact(
        contact_id="contact-10",
        department_id="dep-1",
        comments="Lead qualificado e pronto para comercial.",
    )

    assert seen_request["path"] == "/api/v1/contacts/contact-10/ticket/transfer"
    assert seen_request["method"] == "POST"
    assert '"departmentId":"dep-1"' in seen_request["body"]
    assert '"comments":"Lead qualificado e pronto para comercial."' in seen_request["body"]
    assert response_payload == {"status": "queued"}


@pytest.mark.asyncio
async def test_find_contact_by_phone_rejects_empty_phone() -> None:
    """Falha cedo quando telefone nao e informado no lookup."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"data": []})

    client = CRMClient(http_client=_build_http_client(handler))

    with pytest.raises(ValueError) as exc_info:
        await client.find_contact_by_phone("   ")

    assert "telefone" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_transfer_contact_rejects_empty_required_fields() -> None:
    """Falha cedo quando campos obrigatorios de transferencia estao vazios."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"ok": True})

    client = CRMClient(http_client=_build_http_client(handler))

    with pytest.raises(ValueError) as contact_exc:
        await client.transfer_contact(contact_id=" ", department_id="dep-1", comments="comentario")
    assert "contact_id" in str(contact_exc.value)

    with pytest.raises(ValueError) as department_exc:
        await client.transfer_contact(contact_id="c-1", department_id=" ", comments="comentario")
    assert "department_id" in str(department_exc.value)

    with pytest.raises(ValueError) as comments_exc:
        await client.transfer_contact(contact_id="c-1", department_id="dep-1", comments=" ")
    assert "comments" in str(comments_exc.value)


@pytest.mark.asyncio
async def test_find_contact_by_phone_raises_contract_error_for_invalid_data_shape() -> None:
    """Levanta erro de contrato quando payload de lookup retorna `data` invalido."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"data": {"id": "c-1"}})

    client = CRMClient(http_client=_build_http_client(handler))

    with pytest.raises(IntegrationContractError) as exc_info:
        await client.find_contact_by_phone("+5531999999999")

    assert "campo `data`" in str(exc_info.value)


@pytest.mark.asyncio
async def test_transfer_contact_raises_contract_error_for_non_object_response() -> None:
    """Levanta erro de contrato quando transferencia retorna lista em vez de objeto."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json=[{"status": "ok"}])

    client = CRMClient(http_client=_build_http_client(handler))

    with pytest.raises(IntegrationContractError) as exc_info:
        await client.transfer_contact(contact_id="c-1", department_id="dep-1", comments="ok")

    assert "esperado objeto json" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_build_crm_client_retries_on_policy_status_408(monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante aplicacao da politica de retry do CRM para status 408."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(status_code=408, request=request, json={"error": "timeout"})

        return httpx.Response(status_code=200, request=request, json={"data": [{"id": "c-321"}]})

    monkeypatch.setattr(settings, "crm_base_url", "https://crm.example.com/api/v1")
    monkeypatch.setattr(settings, "crm_token", "crm-token")
    monkeypatch.setattr(settings, "crm_auth_header_name", "Authorization")
    monkeypatch.setattr(settings, "crm_auth_header_prefix", "Bearer")
    monkeypatch.setattr(settings, "crm_contacts_lookup_path", "/contacts")
    monkeypatch.setattr(settings, "crm_lookup_phone_param", "phone")
    monkeypatch.setattr(settings, "crm_lookup_phone_value_template", "{phone}")
    monkeypatch.setattr(settings, "crm_lookup_service_id_param", "serviceId")
    monkeypatch.setattr(settings, "crm_service_id", None)
    monkeypatch.setattr(settings, "crm_transfer_path_template", "/contacts/{contact_id}/ticket/transfer")
    monkeypatch.setattr(settings, "http_timeout_seconds", 5.0)
    monkeypatch.setattr(settings, "http_max_retries", 1)
    monkeypatch.setattr(settings, "http_retry_backoff_seconds", 0.0)

    client = build_crm_client(transport=httpx.MockTransport(handler))
    contact = await client.find_contact_by_phone("+5531555555555")

    assert attempts == 2
    assert contact is not None
    assert contact.contact_id == "c-321"
