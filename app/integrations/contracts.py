"""Validacao de contratos HTTP de integracoes externas."""

from typing import Any

import httpx


class IntegrationContractError(RuntimeError):
    """Erro de contrato quando payload HTTP nao segue formato esperado."""


def parse_json_payload(response: httpx.Response, *, integration_name: str) -> dict[str, Any] | list[Any]:
    """Parseia payload JSON aceitando objeto ou lista; falha para outros tipos."""
    if not response.content:
        return {}

    try:
        payload = response.json()
    except ValueError as exc:
        raise IntegrationContractError(
            f"Resposta JSON invalida em integracao {integration_name}: status={response.status_code}"
        ) from exc

    if isinstance(payload, dict) or isinstance(payload, list):
        return payload

    raise IntegrationContractError(
        "Tipo de payload nao suportado em integracao "
        f"{integration_name}: esperado dict/list, recebido {type(payload).__name__}"
    )


def parse_json_object_payload(
    response: httpx.Response,
    *,
    integration_name: str,
    allow_empty_body: bool = True,
) -> dict[str, Any]:
    """Parseia payload garantindo objeto JSON no resultado final."""
    if not response.content:
        if allow_empty_body:
            return {}

        raise IntegrationContractError(
            f"Resposta vazia nao permitida para integracao {integration_name}: status={response.status_code}"
        )

    payload = parse_json_payload(response, integration_name=integration_name)
    if isinstance(payload, dict):
        return payload

    raise IntegrationContractError(
        f"Payload inesperado em integracao {integration_name}: esperado objeto JSON e recebido lista"
    )
