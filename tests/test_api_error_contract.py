"""Testes do padrao de erro observavel/auditavel da API (fase 8.2)."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_whatsapp_webhook_pipeline_service
from app.main import CORRELATION_ID_HEADER, app
from app.preprocessing import EventNormalizationError


@contextmanager
def _client_with_pipeline_override(
    override: type[Any], *, raise_server_exceptions: bool = True
) -> Iterator[TestClient]:
    app.dependency_overrides[get_whatsapp_webhook_pipeline_service] = override
    client = TestClient(app, raise_server_exceptions=raise_server_exceptions)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()


def test_request_validation_error_uses_standard_error_envelope() -> None:
    """422 de validacao deve seguir payload padronizado e auditavel."""
    client = TestClient(app)

    response = client.post(
        "/webhook/whatsapp",
        headers={CORRELATION_ID_HEADER: "corr-422"},
        json={"body": "invalid"},
    )

    assert response.status_code == 422
    assert response.headers[CORRELATION_ID_HEADER] == "corr-422"
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "request.validation_error"
    assert payload["error"]["error_type"] == "RequestValidationError"
    assert payload["error"]["correlation_id"] == "corr-422"
    assert payload["error"]["path"] == "/webhook/whatsapp"
    assert payload["error"]["method"] == "POST"
    assert isinstance(payload["error"]["details"], list)


def test_application_error_uses_standard_error_envelope() -> None:
    """Erro de normalizacao deve virar `webhook.normalization_error` com detalhes."""

    class _FailingNormalizationPipeline:
        async def process(self, raw_payload: dict[str, Any]) -> Any:
            raise EventNormalizationError("Campo obrigatorio ausente no payload: session_id.")

    with _client_with_pipeline_override(_FailingNormalizationPipeline) as client:
        response = client.post(
            "/webhook/whatsapp",
            headers={CORRELATION_ID_HEADER: "corr-normalization"},
            json={
                "sessionId": "sessao-123",
                "contact": {"phonenumber": "+5531999999999"},
                "lastMessage": {"id": "msg-1", "type": "TEXT", "text": "Oi"},
            },
        )

    assert response.status_code == 422
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "webhook.normalization_error"
    assert payload["error"]["error_type"] == "ApiApplicationError"
    assert payload["error"]["correlation_id"] == "corr-normalization"
    assert payload["error"]["details"]["reason"] == "Campo obrigatorio ausente no payload: session_id."


def test_unexpected_error_uses_internal_error_envelope() -> None:
    """Excecoes inesperadas devem retornar envelope 500 sem vazar detalhes internos."""

    class _ExplodingPipeline:
        async def process(self, raw_payload: dict[str, Any]) -> Any:
            raise RuntimeError("db exploded")

    with _client_with_pipeline_override(_ExplodingPipeline, raise_server_exceptions=False) as client:
        response = client.post(
            "/webhook/whatsapp",
            headers={CORRELATION_ID_HEADER: "corr-500"},
            json={
                "sessionId": "sessao-123",
                "contact": {"phonenumber": "+5531999999999"},
                "lastMessage": {"id": "msg-1", "type": "TEXT", "text": "Oi"},
            },
        )

    assert response.status_code == 500
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "internal.unexpected_error"
    assert payload["error"]["error_type"] == "RuntimeError"
    assert payload["error"]["message"] == "Unexpected server error."
    assert payload["error"]["correlation_id"] == "corr-500"
    assert payload["error"].get("details") is None


def test_not_found_error_uses_http_error_code_format() -> None:
    """404 de rota inexistente deve seguir envelope padronizado."""
    client = TestClient(app)

    response = client.get("/missing-path")

    assert response.status_code == 404
    payload = response.json()
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "http.404"
    assert payload["error"]["path"] == "/missing-path"
    assert payload["error"]["method"] == "GET"
