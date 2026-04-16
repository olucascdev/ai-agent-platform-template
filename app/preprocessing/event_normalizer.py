"""Normalizacao de eventos de webhook para formato canonico interno."""

from dataclasses import dataclass
from typing import Any, Literal

InputType = Literal["text", "audio", "image", "pdf", "other"]


class EventNormalizationError(RuntimeError):
    """Erro quando payload de entrada nao atende contrato minimo."""


@dataclass(frozen=True, slots=True)
class NormalizedAttachment:
    """Representa arquivo de entrada em formato padronizado."""

    mime_type: str
    public_url: str | None
    file_name: str | None
    file_id: str | None


@dataclass(frozen=True, slots=True)
class NormalizedIncomingEvent:
    """Evento canonico usado pelo pipeline de preprocessamento."""

    session_id: str
    contact_phone: str
    input_type: InputType
    text: str | None
    attachments: list[NormalizedAttachment]
    message_id: str | None
    message_created_at: str | None
    message_type_raw: str | None
    contact_name: str | None
    channel_platform: str | None


def normalize_incoming_event(payload: dict[str, Any]) -> NormalizedIncomingEvent:
    """Converte payload bruto em evento canonico interno validado."""
    event_root = _resolve_event_root(payload)

    session_id = _extract_string(event_root.get("sessionId"))
    if session_id is None:
        session_id = _extract_string(_extract_dict(event_root.get("session")).get("id"))
    if session_id is None:
        raise EventNormalizationError("Campo obrigatorio ausente no payload: session_id.")

    contact = _extract_dict(event_root.get("contact"))
    contact_phone = _extract_string(contact.get("phonenumber"))
    if contact_phone is None:
        contact_phone = _extract_string(contact.get("phone"))
    if contact_phone is None:
        contact_phone = _extract_string(contact.get("number"))
    if contact_phone is None:
        raise EventNormalizationError("Campo obrigatorio ausente no payload: contact_phone.")

    last_message = _extract_dict(event_root.get("lastMessage"))
    aggregated = _extract_dict(event_root.get("lastMessagesAggregated"))
    text = _extract_message_text(last_message=last_message, aggregated=aggregated)
    attachments = _extract_attachments(last_message=last_message, aggregated=aggregated)

    message_type_raw = _extract_string(last_message.get("type"))
    input_type = _resolve_input_type(message_type_raw=message_type_raw, text=text, attachments=attachments)

    return NormalizedIncomingEvent(
        session_id=session_id,
        contact_phone=contact_phone,
        input_type=input_type,
        text=text,
        attachments=attachments,
        message_id=_extract_string(last_message.get("id")),
        message_created_at=_extract_string(last_message.get("createdAt")),
        message_type_raw=message_type_raw,
        contact_name=_extract_string(contact.get("name")),
        channel_platform=_extract_string(_extract_dict(event_root.get("channel")).get("platform")),
    )


def _resolve_event_root(payload: dict[str, Any]) -> dict[str, Any]:
    body = payload.get("body")
    if isinstance(body, dict):
        return body

    return payload


def _extract_message_text(*, last_message: dict[str, Any], aggregated: dict[str, Any]) -> str | None:
    aggregated_text = _extract_string(aggregated.get("text"))
    if aggregated_text is not None:
        return aggregated_text

    return _extract_string(last_message.get("text"))


def _extract_attachments(*, last_message: dict[str, Any], aggregated: dict[str, Any]) -> list[NormalizedAttachment]:
    attachments: list[NormalizedAttachment] = []
    dedupe_keys: set[tuple[str, str | None, str | None]] = set()

    aggregated_files = aggregated.get("files")
    if isinstance(aggregated_files, list):
        for file_payload in aggregated_files:
            parsed = _parse_attachment(file_payload)
            if parsed is None:
                continue

            dedupe_key = (parsed.mime_type, parsed.public_url, parsed.file_id)
            if dedupe_key in dedupe_keys:
                continue

            dedupe_keys.add(dedupe_key)
            attachments.append(parsed)

    parsed_last_message_file = _parse_attachment(last_message.get("file"))
    if parsed_last_message_file is not None:
        dedupe_key = (
            parsed_last_message_file.mime_type,
            parsed_last_message_file.public_url,
            parsed_last_message_file.file_id,
        )
        if dedupe_key not in dedupe_keys:
            attachments.append(parsed_last_message_file)

    return attachments


def _parse_attachment(payload: Any) -> NormalizedAttachment | None:
    if not isinstance(payload, dict):
        return None

    mime_type = _extract_string(payload.get("mimeType"))
    public_url = _extract_string(payload.get("publicUrl"))
    file_name = _extract_string(payload.get("name"))
    file_id = _extract_string(payload.get("id"))

    if mime_type is None and public_url is None and file_name is None and file_id is None:
        return None

    return NormalizedAttachment(
        mime_type=mime_type or "application/octet-stream",
        public_url=public_url,
        file_name=file_name,
        file_id=file_id,
    )


def _resolve_input_type(
    *,
    message_type_raw: str | None,
    text: str | None,
    attachments: list[NormalizedAttachment],
) -> InputType:
    if attachments:
        return _resolve_input_type_from_mime(attachments[0].mime_type)

    message_type_upper = (message_type_raw or "").strip().upper()
    if message_type_upper in {"AUDIO", "PTT", "VOICE"}:
        return "audio"
    if message_type_upper in {"IMAGE", "PHOTO"}:
        return "image"
    if message_type_upper == "PDF":
        return "pdf"
    if text is not None:
        return "text"

    return "other"


def _resolve_input_type_from_mime(mime_type: str) -> InputType:
    mime_lower = mime_type.lower()
    if mime_lower.startswith("audio/"):
        return "audio"
    if mime_lower.startswith("image/"):
        return "image"
    if mime_lower == "application/pdf":
        return "pdf"

    return "other"


def _extract_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    return {}


def _extract_string(value: Any) -> str | None:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return normalized
        return None

    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None
