"""Integracoes externas e utilitarios HTTP compartilhados."""

from app.integrations.contracts import IntegrationContractError, parse_json_object_payload, parse_json_payload
from app.integrations.crm_client import CRMClient, CRMContact, build_crm_client
from app.integrations.http_client import (
    HttpClientError,
    HttpClientRequestError,
    HttpClientResponseError,
    ResilientHttpClient,
)
from app.integrations.retry_policy import (
    CRM_RETRY_STATUS_CODES,
    WHATSAPP_SENDER_RETRY_STATUS_CODES,
    RetryPolicy,
    build_crm_retry_policy,
    build_whatsapp_sender_retry_policy,
)
from app.integrations.whatsapp_sender_client import (
    WhatsAppSendResult,
    WhatsAppSenderClient,
    build_whatsapp_sender_client,
)

__all__ = [
    "CRMClient",
    "CRMContact",
    "HttpClientError",
    "HttpClientRequestError",
    "HttpClientResponseError",
    "IntegrationContractError",
    "CRM_RETRY_STATUS_CODES",
    "ResilientHttpClient",
    "RetryPolicy",
    "WHATSAPP_SENDER_RETRY_STATUS_CODES",
    "WhatsAppSendResult",
    "WhatsAppSenderClient",
    "build_crm_client",
    "build_crm_retry_policy",
    "build_whatsapp_sender_client",
    "build_whatsapp_sender_retry_policy",
    "parse_json_object_payload",
    "parse_json_payload",
]
