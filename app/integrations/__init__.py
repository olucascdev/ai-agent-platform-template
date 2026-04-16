"""Integracoes externas e utilitarios HTTP compartilhados."""

from app.integrations.http_client import (
    HttpClientError,
    HttpClientRequestError,
    HttpClientResponseError,
    ResilientHttpClient,
)

__all__ = [
    "HttpClientError",
    "HttpClientRequestError",
    "HttpClientResponseError",
    "ResilientHttpClient",
]
