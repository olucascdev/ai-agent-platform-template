"""Cliente de envio WhatsApp configuravel via HTTP."""

from dataclasses import dataclass
import re
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.config import settings
from app.integrations.contracts import parse_json_payload
from app.integrations.http_client import ResilientHttpClient
from app.integrations.retry_policy import build_whatsapp_sender_retry_policy


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
        include_number_field: bool = True,
        number_field: str = "number",
        text_field: str = "text",
    ) -> None:
        self._http_client = http_client
        self._send_path_template = send_path
        self._method = method.upper()
        self._include_number_field = include_number_field
        self._number_field = number_field
        self._text_field = text_field

    async def send_text(self, *, phone: str, text: str, session_id: str | None = None) -> WhatsAppSendResult:
        """Envia mensagem de texto para numero de telefone informado."""
        normalized_phone = phone.strip()
        normalized_text = text.strip()
        normalized_session_id = session_id.strip() if isinstance(session_id, str) else None
        if not normalized_phone:
            raise ValueError("Telefone deve ser informado para envio de mensagem no sender WhatsApp.")
        if not normalized_text:
            raise ValueError("Texto deve ser informado para envio de mensagem no sender WhatsApp.")

        send_path = self._render_send_path(phone=normalized_phone, session_id=normalized_session_id)
        payload: dict[str, str] = {self._text_field: normalized_text}
        if self._include_number_field:
            payload[self._number_field] = normalized_phone

        response = await self._http_client.request(
            self._method,
            send_path,
            json_body=payload,
        )

        return WhatsAppSendResult(status_code=response.status_code, payload=self._parse_json_response(response))

    def _render_send_path(self, *, phone: str, session_id: str | None) -> str:
        path = self._send_path_template
        replacements: dict[str, str] = {
            "phone": phone,
            "number": phone,
        }
        if session_id:
            replacements["session_id"] = session_id
            replacements["sessionId"] = session_id

        for placeholder, value in replacements.items():
            path = path.replace(f"{{{placeholder}}}", value)

        unresolved_placeholders = sorted(set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", path)))
        if unresolved_placeholders:
            raise ValueError(
                "WHATSAPP_SENDER_URL contem placeholders sem valor. "
                f"Resolva as chaves: {', '.join(unresolved_placeholders)}."
            )

        return path

    def _parse_json_response(self, response: httpx.Response) -> dict[str, Any]:
        payload = parse_json_payload(response, integration_name="whatsapp_sender.send_text")
        if isinstance(payload, dict):
            return payload

        return {"data": payload}


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

    retry_policy = build_whatsapp_sender_retry_policy(
        max_retries=settings.http_max_retries,
        retry_backoff_seconds=settings.http_retry_backoff_seconds,
    )

    base_url, send_path = _split_sender_url(settings.whatsapp_sender_url)
    http_client = ResilientHttpClient(
        base_url=base_url,
        default_headers={settings.whatsapp_sender_auth_header_name: auth_value},
        timeout_seconds=settings.http_timeout_seconds,
        max_retries=retry_policy.max_retries,
        retry_backoff_seconds=retry_policy.retry_backoff_seconds,
        retry_status_codes=retry_policy.retry_status_codes,
        transport=transport,
    )

    return WhatsAppSenderClient(
        http_client=http_client,
        send_path=send_path,
        method=settings.whatsapp_sender_method,
        include_number_field=settings.whatsapp_sender_include_number,
        number_field=settings.whatsapp_sender_number_field,
        text_field=settings.whatsapp_sender_text_field,
    )
