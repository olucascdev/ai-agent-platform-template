"""Testes do cliente HTTP resiliente da fase 4.1."""

import logging

import httpx
import pytest

from app.integrations.http_client import (
    HttpClientRequestError,
    HttpClientResponseError,
    ResilientHttpClient,
)


@pytest.mark.asyncio
async def test_http_client_returns_success_response_without_retry() -> None:
    """Retorna resposta 2xx diretamente quando a primeira tentativa da certo."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, request=request, json={"ok": True})

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=2,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_http_client_retries_retryable_status_and_then_succeeds() -> None:
    """Aplica retry para status retryavel e conclui com sucesso quando a API se recupera."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(status_code=503, request=request, text="temporariamente indisponivel")

        return httpx.Response(status_code=200, request=request, json={"result": "ok"})

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=2,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("POST", "/contacts", json_body={"name": "Luna"})

    assert attempts == 2
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}


@pytest.mark.asyncio
async def test_http_client_raises_response_error_after_retry_exhaustion() -> None:
    """Lanca erro de resposta quando esgota retries para status retryavel."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(status_code=503, request=request, text="falha persistente")

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=1,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(HttpClientResponseError) as exc_info:
        await client.request("GET", "/health")

    assert attempts == 2
    assert exc_info.value.status_code == 503
    assert exc_info.value.retryable is True
    assert "GET https://api.example.com/health" in str(exc_info.value)


@pytest.mark.asyncio
async def test_http_client_does_not_retry_non_retryable_status() -> None:
    """Nao executa retry quando a resposta nao faz parte da politica de retry."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(status_code=400, request=request, text="payload invalido")

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=3,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(HttpClientResponseError) as exc_info:
        await client.request("POST", "/contacts", json_body={"name": ""})

    assert attempts == 1
    assert exc_info.value.status_code == 400
    assert exc_info.value.retryable is False


@pytest.mark.asyncio
async def test_http_client_retries_request_error_and_can_recover() -> None:
    """Executa retry para erro de rede e finaliza com sucesso quando a conexao volta."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectError("falha de rede", request=request)

        return httpx.Response(status_code=200, request=request, json={"ok": True})

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=2,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    response = await client.request("GET", "/health")

    assert attempts == 2
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_http_client_raises_request_error_after_network_retry_exhaustion() -> None:
    """Lanca erro especifico quando falha de rede persiste apos retries."""

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("tempo esgotado", request=request)

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        max_retries=1,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(HttpClientRequestError) as exc_info:
        await client.request("GET", "/health")

    assert "falha de rede" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_http_client_redacts_sensitive_headers_in_warning_logs(caplog: pytest.LogCaptureFixture) -> None:
    """Garante que logs de retry nao exponham tokens sensiveis."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(status_code=503, request=request, text="indisponivel")

        return httpx.Response(status_code=200, request=request, json={"ok": True})

    client = ResilientHttpClient(
        base_url="https://api.example.com",
        default_headers={
            "Authorization": "Bearer super-secret-token",
            "token": "abc123",
            "X-Trace-Id": "trace-1",
        },
        max_retries=1,
        retry_backoff_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    with caplog.at_level(logging.WARNING):
        response = await client.request("GET", "/health")

    assert response.status_code == 200
    assert "super-secret-token" not in caplog.text
    assert "abc123" not in caplog.text
    assert "<redacted>" in caplog.text
