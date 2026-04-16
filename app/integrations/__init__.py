"""Integracoes externas e utilitarios HTTP compartilhados."""

from app.integrations.crm_client import CRMClient, CRMContact, build_crm_client
from app.integrations.http_client import (
    HttpClientError,
    HttpClientRequestError,
    HttpClientResponseError,
    ResilientHttpClient,
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
    "ResilientHttpClient",
    "WhatsAppSendResult",
    "WhatsAppSenderClient",
    "build_crm_client",
    "build_whatsapp_sender_client",
]
