"""Testes do cliente de sender WhatsApp configuravel da fase 4.3."""

from collections.abc import Callable
from typing import Any

import httpx
import pytest

from app.config import settings
from app.integrations.contracts import IntegrationContractError
from app.integrations.http_client import ResilientHttpClient
from app.integrations.whatsapp_sender_client import (
    WhatsAppSenderClient,
    _split_sender_url,
    build_whatsapp_sender_client,
)


def _build_http_client(handler: Callable[[httpx.Request], httpx.Response]) -> ResilientHttpClient:
    return ResilientHttpClient(
        base_url="https://sender.example.com",
        default_headers={"Authorization": "Bearer test-token"},
        timeout_seconds=10,
        max_retries=0,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_sender_client_sends_default_payload_fields() -> None:
    """Valida envio usando campos padrao `number` e `text`."""
    seen_request: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_request["method"] = request.method
        seen_request["path"] = request.url.path
        seen_request["body"] = request.content.decode("utf-8")
        seen_request["auth"] = request.headers.get("Authorization")
        return httpx.Response(status_code=200, request=request, json={"queued": True})

    client = WhatsAppSenderClient(
        http_client=_build_http_client(handler),
        send_path="/send/text",
    )

    result = await client.send_text(phone="+5531999999999", text="Ola! Tudo bem?")

    assert seen_request["method"] == "POST"
    assert seen_request["path"] == "/send/text"
    assert '"number":"+5531999999999"' in seen_request["body"]
    assert '"text":"Ola! Tudo bem?"' in seen_request["body"]
    assert seen_request["auth"] == "Bearer test-token"
    assert result.status_code == 200
    assert result.payload == {"queued": True}


@pytest.mark.asyncio
async def test_sender_client_supports_custom_method_and_payload_fields() -> None:
    """Permite adaptar metodo HTTP e chaves de payload para provedores diferentes."""
    seen_request: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_request["method"] = request.method
        seen_request["body"] = request.content.decode("utf-8")
        return httpx.Response(status_code=202, request=request, json={"accepted": True})

    client = WhatsAppSenderClient(
        http_client=_build_http_client(handler),
        send_path="/v2/messages",
        method="put",
        number_field="to",
        text_field="message",
    )

    result = await client.send_text(phone="+5531888888888", text="Mensagem customizada")

    assert seen_request["method"] == "PUT"
    assert '"to":"+5531888888888"' in seen_request["body"]
    assert '"message":"Mensagem customizada"' in seen_request["body"]
    assert result.status_code == 202
    assert result.payload == {"accepted": True}


@pytest.mark.asyncio
async def test_sender_client_returns_empty_payload_for_empty_response_body() -> None:
    """Retorna payload vazio quando provedor responde sem corpo."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=204, request=request, content=b"")

    client = WhatsAppSenderClient(
        http_client=_build_http_client(handler),
        send_path="/send/text",
    )

    result = await client.send_text(phone="+5531777777777", text="Ping")

    assert result.status_code == 204
    assert result.payload == {}


@pytest.mark.asyncio
async def test_sender_client_rejects_empty_phone_or_text() -> None:
    """Falha cedo quando telefone ou texto estao vazios."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"ok": True})

    client = WhatsAppSenderClient(http_client=_build_http_client(handler), send_path="/send/text")

    with pytest.raises(ValueError) as phone_exc:
        await client.send_text(phone="   ", text="mensagem")
    assert "telefone" in str(phone_exc.value).lower()

    with pytest.raises(ValueError) as text_exc:
        await client.send_text(phone="+5531999999999", text="   ")
    assert "texto" in str(text_exc.value).lower()


@pytest.mark.asyncio
async def test_sender_client_raises_contract_error_for_primitive_json_response() -> None:
    """Levanta erro de contrato quando provider retorna tipo JSON nao suportado."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json=123)

    client = WhatsAppSenderClient(http_client=_build_http_client(handler), send_path="/send/text")

    with pytest.raises(IntegrationContractError) as exc_info:
        await client.send_text(phone="+5531999999999", text="ok")

    assert "tipo de payload nao suportado" in str(exc_info.value).lower()


def test_split_sender_url_supports_path_and_query_string() -> None:
    """Separa corretamente URL completa para base URL e path final."""
    base_url, path = _split_sender_url("https://sender.example.com/send/text?channel=main")

    assert base_url == "https://sender.example.com"
    assert path == "/send/text?channel=main"


def test_split_sender_url_raises_for_invalid_url() -> None:
    """Falha com erro explicito para URL de sender invalida."""
    with pytest.raises(ValueError) as exc_info:
        _split_sender_url("sender-sem-protocolo")

    assert "WHATSAPP_SENDER_URL invalida" in str(exc_info.value)


@pytest.mark.asyncio
async def test_build_sender_client_uses_settings_for_auth_and_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monta cliente com contrato de auth/payload baseado nas configuracoes."""
    seen_request: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_request["path"] = request.url.path
        seen_request["query"] = request.url.query.decode("utf-8")
        seen_request["auth_header"] = request.headers.get("token")
        seen_request["body"] = request.content.decode("utf-8")
        return httpx.Response(status_code=200, request=request, json={"id": "msg-1"})

    monkeypatch.setattr(settings, "whatsapp_sender_url", "https://sender.example.com/send/text?instance=a1")
    monkeypatch.setattr(settings, "whatsapp_sender_method", "POST")
    monkeypatch.setattr(settings, "whatsapp_sender_number_field", "number")
    monkeypatch.setattr(settings, "whatsapp_sender_text_field", "text")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_name", "token")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_prefix", "")
    monkeypatch.setattr(settings, "whatsapp_token", "token-cru")

    client = build_whatsapp_sender_client(transport=httpx.MockTransport(handler))
    result = await client.send_text(phone="+5531666666666", text="Teste sender")

    assert seen_request["path"] == "/send/text"
    assert seen_request["query"] == "instance=a1"
    assert seen_request["auth_header"] == "token-cru"
    assert '"number":"+5531666666666"' in seen_request["body"]
    assert '"text":"Teste sender"' in seen_request["body"]
    assert result.payload == {"id": "msg-1"}


@pytest.mark.asyncio
async def test_build_sender_client_retries_on_policy_status_425(monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante aplicacao da politica de retry do sender para status 425."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(status_code=425, request=request, json={"error": "too early"})

        return httpx.Response(status_code=200, request=request, json={"id": "msg-44"})

    monkeypatch.setattr(settings, "whatsapp_sender_url", "https://sender.example.com/send/text")
    monkeypatch.setattr(settings, "whatsapp_sender_method", "POST")
    monkeypatch.setattr(settings, "whatsapp_sender_number_field", "number")
    monkeypatch.setattr(settings, "whatsapp_sender_text_field", "text")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_name", "Authorization")
    monkeypatch.setattr(settings, "whatsapp_sender_auth_header_prefix", "Bearer")
    monkeypatch.setattr(settings, "whatsapp_token", "sender-token")
    monkeypatch.setattr(settings, "http_timeout_seconds", 5.0)
    monkeypatch.setattr(settings, "http_max_retries", 1)
    monkeypatch.setattr(settings, "http_retry_backoff_seconds", 0.0)

    client = build_whatsapp_sender_client(transport=httpx.MockTransport(handler))
    result = await client.send_text(phone="+5531444444444", text="mensagem")

    assert attempts == 2
    assert result.payload == {"id": "msg-44"}
