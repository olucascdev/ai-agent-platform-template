"""Testes da feature 5.1 de normalizacao de evento canonico."""

import pytest

from app.preprocessing import EventNormalizationError, normalize_incoming_event


def test_normalize_text_event_from_webhook_wrapper() -> None:
    """Normaliza payload de texto vindo no formato com chave `body`."""
    payload = {
        "body": {
            "sessionId": "sessao-123",
            "contact": {"phonenumber": "+5531999999999", "name": "Joel"},
            "channel": {"platform": "WhatsApp"},
            "lastMessage": {
                "id": "msg-1",
                "createdAt": "2026-04-16T10:00:00Z",
                "type": "TEXT",
                "text": "  mensagem antiga  ",
            },
            "lastMessagesAggregated": {"text": "  Ola, preciso de ajuda  ", "files": []},
        }
    }

    event = normalize_incoming_event(payload)

    assert event.session_id == "sessao-123"
    assert event.contact_phone == "+5531999999999"
    assert event.text == "Ola, preciso de ajuda"
    assert event.input_type == "text"
    assert event.message_id == "msg-1"
    assert event.channel_platform == "WhatsApp"
    assert event.attachments == []


def test_normalize_audio_event_from_aggregated_file() -> None:
    """Classifica evento como audio quando o anexo possui mime `audio/*`."""
    payload = {
        "session": {"id": "sessao-456"},
        "contact": {"phonenumber": "+5531888888888"},
        "lastMessage": {"type": "AUDIO", "file": None},
        "lastMessagesAggregated": {
            "text": "",
            "files": [
                {
                    "id": "file-a1",
                    "mimeType": "audio/ogg",
                    "publicUrl": "https://cdn.exemplo.com/audio.ogg",
                    "name": "audio.ogg",
                }
            ],
        },
    }

    event = normalize_incoming_event(payload)

    assert event.input_type == "audio"
    assert event.text is None
    assert len(event.attachments) == 1
    assert event.attachments[0].mime_type == "audio/ogg"


def test_normalize_image_event_from_last_message_file_fallback() -> None:
    """Usa `lastMessage.file` quando `lastMessagesAggregated.files` nao existe."""
    payload = {
        "sessionId": "sessao-789",
        "contact": {"phonenumber": "+5531777777777"},
        "lastMessage": {
            "type": "IMAGE",
            "file": {
                "id": "file-img",
                "mimeType": "image/png",
                "publicUrl": "https://cdn.exemplo.com/img.png",
                "name": "img.png",
            },
        },
    }

    event = normalize_incoming_event(payload)

    assert event.input_type == "image"
    assert len(event.attachments) == 1
    assert event.attachments[0].public_url == "https://cdn.exemplo.com/img.png"


def test_normalize_pdf_event_detected_by_mime() -> None:
    """Classifica evento como pdf quando o mime do anexo e `application/pdf`."""
    payload = {
        "sessionId": "sessao-pdf",
        "contact": {"phonenumber": "+5531666666666"},
        "lastMessage": {"type": "DOCUMENT"},
        "lastMessagesAggregated": {
            "text": "Segue o arquivo",
            "files": [
                {
                    "mimeType": "application/pdf",
                    "publicUrl": "https://cdn.exemplo.com/arquivo.pdf",
                }
            ],
        },
    }

    event = normalize_incoming_event(payload)

    assert event.input_type == "pdf"
    assert event.text == "Segue o arquivo"


def test_normalizer_deduplicates_attachments_between_aggregated_and_last_message() -> None:
    """Evita anexos duplicados quando mesmo arquivo aparece em duas origens."""
    payload = {
        "sessionId": "sessao-dup",
        "contact": {"phonenumber": "+5531555555555"},
        "lastMessage": {
            "type": "IMAGE",
            "file": {
                "id": "same-id",
                "mimeType": "image/jpeg",
                "publicUrl": "https://cdn.exemplo.com/dup.jpg",
            },
        },
        "lastMessagesAggregated": {
            "text": "",
            "files": [
                {
                    "id": "same-id",
                    "mimeType": "image/jpeg",
                    "publicUrl": "https://cdn.exemplo.com/dup.jpg",
                }
            ],
        },
    }

    event = normalize_incoming_event(payload)

    assert len(event.attachments) == 1


def test_normalizer_raises_when_session_is_missing() -> None:
    """Falha com erro explicito quando sessao nao e informada."""
    payload = {
        "contact": {"phonenumber": "+5531999999999"},
        "lastMessage": {"type": "TEXT", "text": "oi"},
    }

    with pytest.raises(EventNormalizationError) as exc_info:
        normalize_incoming_event(payload)

    assert "session_id" in str(exc_info.value)


def test_normalizer_raises_when_phone_is_missing() -> None:
    """Falha com erro explicito quando telefone do contato nao existe."""
    payload = {
        "sessionId": "sessao-sem-telefone",
        "contact": {},
        "lastMessage": {"type": "TEXT", "text": "oi"},
    }

    with pytest.raises(EventNormalizationError) as exc_info:
        normalize_incoming_event(payload)

    assert "contact_phone" in str(exc_info.value)
