"""Cliente HTTP resiliente para integracoes externas configuraveis."""

import asyncio
import logging
from collections.abc import Mapping
from typing import Any

import httpx

SENSITIVE_HEADERS = {
    "authorization",
    "proxy-authorization",
    "token",
    "x-api-key",
    "api-key",
    "x-auth-token",
}


class HttpClientError(RuntimeError):
    """Erro base do cliente HTTP resiliente."""


class HttpClientRequestError(HttpClientError):
    """Erro de rede/conexao apos esgotar tentativas de retry."""


class HttpClientResponseError(HttpClientError):
    """Erro de resposta HTTP 4xx/5xx."""

    def __init__(
        self,
        *,
        method: str,
        url: str,
        status_code: int,
        retryable: bool,
        response_text: str,
    ) -> None:
        self.method = method
        self.url = url
        self.status_code = status_code
        self.retryable = retryable
        self.response_text = response_text
        super().__init__(
            "Erro HTTP ao chamar integracao externa: "
            f"{method} {url} -> status={status_code}, retryable={retryable}, body={response_text}"
        )


class ResilientHttpClient:
    """Encapsula chamadas HTTP com timeout, retry e logs seguros."""

    def __init__(
        self,
        *,
        base_url: str,
        default_headers: Mapping[str, str] | None = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
        retry_backoff_seconds: float = 0.5,
        retry_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
        transport: httpx.AsyncBaseTransport | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._base_url = base_url
        self._default_headers = dict(default_headers or {})
        self._timeout = timeout_seconds
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._retry_status_codes = retry_status_codes
        self._transport = transport
        self._logger = logger or logging.getLogger(__name__)

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Any | None = None,
        data: Mapping[str, Any] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        """Executa request HTTP com politicas padrao de resiliencia."""
        attempts_total = self._max_retries + 1
        request_url = self._build_request_url(path)
        method_upper = method.upper()
        merged_headers = self._merge_headers(headers)
        sanitized_headers = self._sanitize_headers(merged_headers)

        for attempt in range(1, attempts_total + 1):
            try:
                async with httpx.AsyncClient(
                    base_url=self._base_url,
                    timeout=self._timeout,
                    transport=self._transport,
                ) as client:
                    response = await client.request(
                        method=method_upper,
                        url=path,
                        params=params,
                        json=json_body,
                        data=data,
                        headers=merged_headers,
                    )
            except httpx.RequestError as exc:
                if attempt < attempts_total:
                    self._logger.warning(
                        "Erro de rede em integracao externa. tentativa=%s/%s metodo=%s url=%s headers=%s erro=%s",
                        attempt,
                        attempts_total,
                        method_upper,
                        request_url,
                        sanitized_headers,
                        exc.__class__.__name__,
                    )
                    await asyncio.sleep(self._compute_backoff(attempt))
                    continue

                raise HttpClientRequestError(
                    f"Falha de rede ao chamar integracao externa apos retries: {method_upper} {request_url}"
                ) from exc

            should_retry_response = response.status_code in self._retry_status_codes
            if should_retry_response and attempt < attempts_total:
                self._logger.warning(
                    "Resposta HTTP retryavel em integracao externa. tentativa=%s/%s metodo=%s url=%s status=%s headers=%s",
                    attempt,
                    attempts_total,
                    method_upper,
                    request_url,
                    response.status_code,
                    sanitized_headers,
                )
                await asyncio.sleep(self._compute_backoff(attempt))
                continue

            if response.status_code >= 400:
                raise HttpClientResponseError(
                    method=method_upper,
                    url=request_url,
                    status_code=response.status_code,
                    retryable=should_retry_response,
                    response_text=self._truncate_text(response.text),
                )

            return response

        raise RuntimeError("Fluxo inesperado no cliente HTTP resiliente.")

    def _compute_backoff(self, attempt: int) -> float:
        return self._retry_backoff_seconds * (2 ** (attempt - 1))

    def _build_request_url(self, path: str) -> str:
        return f"{self._base_url.rstrip('/')}/{path.lstrip('/')}"

    def _merge_headers(self, headers: Mapping[str, str] | None) -> dict[str, str]:
        merged = dict(self._default_headers)
        if headers:
            merged.update(headers)
        return merged

    def _sanitize_headers(self, headers: Mapping[str, str]) -> dict[str, str]:
        sanitized: dict[str, str] = {}
        for key, value in headers.items():
            if key.lower() in SENSITIVE_HEADERS:
                sanitized[key] = "<redacted>"
                continue

            sanitized[key] = value

        return sanitized

    def _truncate_text(self, text: str, max_chars: int = 300) -> str:
        if len(text) <= max_chars:
            return text

        return f"{text[:max_chars]}..."
