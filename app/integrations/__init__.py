"""Integracoes externas e utilitarios HTTP compartilhados."""

from app.integrations.crm_client import CRMClient, CRMContact, build_crm_client
from app.integrations.http_client import (
    HttpClientError,
    HttpClientRequestError,
    HttpClientResponseError,
    ResilientHttpClient,
)

__all__ = [
    "CRMClient",
    "CRMContact",
    "HttpClientError",
    "HttpClientRequestError",
    "HttpClientResponseError",
    "ResilientHttpClient",
    "build_crm_client",
]
