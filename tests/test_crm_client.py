"""Testes do cliente de CRM configuravel da fase 4.2."""

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.integrations.crm_client import CRMClient
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
