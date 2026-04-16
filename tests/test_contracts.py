"""Testes da camada de validacao de contrato HTTP das integracoes."""

import httpx
import pytest

from app.integrations.contracts import IntegrationContractError, parse_json_object_payload, parse_json_payload


def test_parse_json_payload_returns_dict_or_list() -> None:
    """Aceita apenas payload JSON em formato objeto ou lista."""
    request = httpx.Request("GET", "https://api.example.com")

    dict_response = httpx.Response(status_code=200, request=request, json={"ok": True})
    list_response = httpx.Response(status_code=200, request=request, json=[{"id": "1"}])

    assert parse_json_payload(dict_response, integration_name="teste") == {"ok": True}
    assert parse_json_payload(list_response, integration_name="teste") == [{"id": "1"}]


def test_parse_json_payload_raises_for_invalid_type() -> None:
    """Falha para tipos primitivos que nao fazem parte do contrato."""
    request = httpx.Request("GET", "https://api.example.com")
    response = httpx.Response(status_code=200, request=request, json="texto")

    with pytest.raises(IntegrationContractError) as exc_info:
        parse_json_payload(response, integration_name="teste")

    assert "tipo de payload" in str(exc_info.value).lower()


def test_parse_json_object_payload_allows_empty_only_when_enabled() -> None:
    """Controla resposta vazia conforme configuracao da integracao."""
    request = httpx.Request("POST", "https://api.example.com")
    empty_response = httpx.Response(status_code=204, request=request, content=b"")

    assert parse_json_object_payload(empty_response, integration_name="teste", allow_empty_body=True) == {}

    with pytest.raises(IntegrationContractError) as exc_info:
        parse_json_object_payload(empty_response, integration_name="teste", allow_empty_body=False)

    assert "resposta vazia" in str(exc_info.value).lower()


def test_parse_json_object_payload_raises_for_list_payload() -> None:
    """Falha quando contrato exige objeto e a API retorna lista."""
    request = httpx.Request("POST", "https://api.example.com")
    list_response = httpx.Response(status_code=200, request=request, json=[{"ok": True}])

    with pytest.raises(IntegrationContractError) as exc_info:
        parse_json_object_payload(list_response, integration_name="teste")

    assert "esperado objeto" in str(exc_info.value).lower()
