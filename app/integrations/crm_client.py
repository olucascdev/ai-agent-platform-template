"""Cliente de CRM configuravel para lookup de contatos e transferencia."""

from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings
from app.integrations.contracts import IntegrationContractError, parse_json_object_payload, parse_json_payload
from app.integrations.http_client import ResilientHttpClient
from app.integrations.retry_policy import build_crm_retry_policy


@dataclass(slots=True)
class CRMContact:
    """Representa o contato retornado pela API do CRM."""

    contact_id: str
    raw: dict[str, Any]


class CRMClient:
    """Encapsula operacoes principais do CRM usadas pelo fluxo conversacional."""

    def __init__(
        self,
        *,
        http_client: ResilientHttpClient,
        contacts_lookup_path: str = "/contacts",
        lookup_phone_param: str = "phone",
        lookup_phone_value_template: str = "{phone}",
        lookup_service_id_param: str = "serviceId",
        service_id: str | None = None,
        transfer_path_template: str = "/contacts/{contact_id}/ticket/transfer",
    ) -> None:
        self._http_client = http_client
        self._contacts_lookup_path = contacts_lookup_path
        self._lookup_phone_param = lookup_phone_param
        self._lookup_phone_value_template = lookup_phone_value_template
        self._lookup_service_id_param = lookup_service_id_param
        self._service_id = service_id
        self._transfer_path_template = transfer_path_template

    async def find_contact_by_phone(self, phone: str) -> CRMContact | None:
        """Busca contato por telefone usando parametros configuraveis."""
        normalized_phone = phone.strip()
        if not normalized_phone:
            raise ValueError("Telefone deve ser informado para busca de contato no CRM.")

        params: dict[str, str] = {
            self._lookup_phone_param: self._lookup_phone_value_template.format(phone=normalized_phone),
        }
        if self._service_id:
            params[self._lookup_service_id_param] = self._service_id

        response = await self._http_client.request(
            "GET",
            self._contacts_lookup_path,
            params=params,
        )
        response_payload = self._parse_lookup_response(response)
        return self._extract_first_contact(response_payload)

    async def transfer_contact(self, *, contact_id: str, department_id: str, comments: str) -> dict[str, Any]:
        """Transfere contato para departamento no CRM."""
        normalized_contact_id = contact_id.strip()
        normalized_department_id = department_id.strip()
        normalized_comments = comments.strip()

        if not normalized_contact_id:
            raise ValueError("contact_id deve ser informado para transferencia no CRM.")
        if not normalized_department_id:
            raise ValueError("department_id deve ser informado para transferencia no CRM.")
        if not normalized_comments:
            raise ValueError("comments deve ser informado para transferencia no CRM.")

        response = await self._http_client.request(
            "POST",
            self._transfer_path_template.format(contact_id=normalized_contact_id),
            json_body={"departmentId": normalized_department_id, "comments": normalized_comments},
        )

        return parse_json_object_payload(response, integration_name="crm.transfer")

    def _parse_lookup_response(self, response: Any) -> dict[str, Any]:
        payload = parse_json_payload(response, integration_name="crm.lookup")
        if isinstance(payload, dict):
            return payload

        return {"data": payload}

    def _extract_first_contact(self, payload: dict[str, Any]) -> CRMContact | None:
        if "id" in payload:
            contact_id = str(payload["id"])
            return CRMContact(contact_id=contact_id, raw=payload)

        contacts = payload.get("data")
        if contacts is None:
            return None

        if not isinstance(contacts, list):
            raise IntegrationContractError("Resposta de lookup CRM invalida: campo `data` deve ser lista.")
        if not contacts:
            return None

        first_contact = contacts[0]
        if not isinstance(first_contact, dict):
            raise IntegrationContractError("Resposta de lookup CRM invalida: primeiro item de `data` nao e objeto.")

        contact_id_value = first_contact.get("id") or first_contact.get("contactId")
        if contact_id_value is None:
            raise IntegrationContractError(
                "Resposta de lookup CRM invalida: contato retornado sem `id` ou `contactId`."
            )

        return CRMContact(contact_id=str(contact_id_value), raw=first_contact)


def build_crm_client(*, transport: httpx.AsyncBaseTransport | None = None) -> CRMClient:
    """Monta cliente CRM com configuracoes centralizadas do ambiente."""
    auth_value = settings.crm_token
    if settings.crm_auth_header_prefix.strip():
        auth_value = f"{settings.crm_auth_header_prefix.strip()} {settings.crm_token}"

    retry_policy = build_crm_retry_policy(
        max_retries=settings.http_max_retries,
        retry_backoff_seconds=settings.http_retry_backoff_seconds,
    )

    http_client = ResilientHttpClient(
        base_url=settings.crm_base_url,
        default_headers={settings.crm_auth_header_name: auth_value},
        timeout_seconds=settings.http_timeout_seconds,
        max_retries=retry_policy.max_retries,
        retry_backoff_seconds=retry_policy.retry_backoff_seconds,
        retry_status_codes=retry_policy.retry_status_codes,
        transport=transport,
    )

    return CRMClient(
        http_client=http_client,
        contacts_lookup_path=settings.crm_contacts_lookup_path,
        lookup_phone_param=settings.crm_lookup_phone_param,
        lookup_phone_value_template=settings.crm_lookup_phone_value_template,
        lookup_service_id_param=settings.crm_lookup_service_id_param,
        service_id=settings.crm_service_id,
        transfer_path_template=settings.crm_transfer_path_template,
    )
