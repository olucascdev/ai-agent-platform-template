"""Cliente de envio WhatsApp configuravel via HTTP."""

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.config import settings
from app.integrations.http_client import ResilientHttpClient


@dataclass(slots=True)
class WhatsAppSendResult:
    """Representa resultado de envio retornado pelo provedor."""

    status_code: int
    payload: dict[str, Any]


class WhatsAppSenderClient:
    """Encapsula envio de texto para provedores HTTP de WhatsApp."""

    def __init__(
        self,
        *,
        http_client: ResilientHttpClient,
        send_path: str,
        method: str = "POST",
        number_field: str = "number",
        text_field: str = "text",
    ) -> None:
        self._http_client = http_client
        self._send_path = send_path
        self._method = method.upper()
        self._number_field = number_field
        self._text_field = text_field

    async def send_text(self, *, phone: str, text: str) -> WhatsAppSendResult:
        """Envia mensagem de texto para numero de telefone informado."""
        response = await self._http_client.request(
            self._method,
            self._send_path,
            json_body={self._number_field: phone, self._text_field: text},
        )

        return WhatsAppSendResult(status_code=response.status_code, payload=self._parse_json_response(response))

    def _parse_json_response(self, response: httpx.Response) -> dict[str, Any]:
        if not response.content:
            return {}

        payload = response.json()
        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list):
            return {"data": payload}

        return {"data": []}


def _split_sender_url(url: str) -> tuple[str, str]:
    """Separa URL completa em base e path para uso no cliente HTTP."""
    parsed = urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("WHATSAPP_SENDER_URL invalida: informe URL completa com protocolo e host.")

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path or "/"
    if parsed.query:
        path = f"{path}?{parsed.query}"

    return base_url, path


def build_whatsapp_sender_client(*, transport: httpx.AsyncBaseTransport | None = None) -> WhatsAppSenderClient:
    """Monta cliente de sender WhatsApp com configuracoes centralizadas."""
    auth_value = settings.whatsapp_token
    if settings.whatsapp_sender_auth_header_prefix.strip():
        auth_value = f"{settings.whatsapp_sender_auth_header_prefix.strip()} {settings.whatsapp_token}"

    base_url, send_path = _split_sender_url(settings.whatsapp_sender_url)
    http_client = ResilientHttpClient(
        base_url=base_url,
        default_headers={settings.whatsapp_sender_auth_header_name: auth_value},
        timeout_seconds=settings.http_timeout_seconds,
        max_retries=settings.http_max_retries,
        retry_backoff_seconds=settings.http_retry_backoff_seconds,
        transport=transport,
    )

    return WhatsAppSenderClient(
        http_client=http_client,
        send_path=send_path,
        method=settings.whatsapp_sender_method,
        number_field=settings.whatsapp_sender_number_field,
        text_field=settings.whatsapp_sender_text_field,
    )
