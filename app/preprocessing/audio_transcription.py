"""Transcricao de audio com provider configuravel para o preprocessor."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent

AudioDownloader = Callable[[str], Awaitable[bytes]]


class AudioTranscriptionError(RuntimeError):
    """Erro base para falhas de transcricao de audio."""


class UnsupportedAudioTranscriptionProviderError(AudioTranscriptionError):
    """Erro quando provider configurado de transcricao nao e suportado."""


class AudioAttachmentNotFoundError(AudioTranscriptionError):
    """Erro quando evento nao contem anexo de audio valido."""


class AudioDownloadError(AudioTranscriptionError):
    """Erro ao baixar arquivo de audio para transcricao."""


@dataclass(frozen=True, slots=True)
class AudioTranscription:
    """Resultado de transcricao com metadados do provider usado."""

    text: str
    provider: str
    model: str


class AudioTranscriber(Protocol):
    """Contrato de provider de transcricao de audio."""

    async def transcribe(self, *, audio_bytes: bytes, mime_type: str, file_name: str | None) -> AudioTranscription:
        """Retorna texto transcrito a partir dos bytes de audio."""


class OpenAIAudioTranscriber:
    """Implementacao de transcricao usando API da OpenAI."""

    def __init__(self, *, model: str, language: str | None = None, client: Any | None = None, api_key: str | None = None, base_url: str | None = None) -> None:
        self._model = model
        self._language = language
        resolved_api_key = api_key or settings.openai_api_key
        self._client: Any = client or AsyncOpenAI(api_key=resolved_api_key, base_url=base_url)

    async def transcribe(self, *, audio_bytes: bytes, mime_type: str, file_name: str | None) -> AudioTranscription:
        """Executa transcricao no provider OpenAI e retorna texto consolidado."""
        if not audio_bytes:
            raise AudioTranscriptionError("Arquivo de audio vazio recebido para transcricao.")

        normalized_file_name = (file_name or "audio_input").strip() or "audio_input"
        request_payload = {
            "model": self._model,
            "file": (normalized_file_name, audio_bytes, mime_type),
        }
        if self._language:
            request_payload["language"] = self._language

        response = await self._client.audio.transcriptions.create(**request_payload)
        raw_text = getattr(response, "text", None)
        if not isinstance(raw_text, str):
            raise AudioTranscriptionError("Provider OpenAI retornou resposta de transcricao sem campo `text` valido.")

        normalized_text = raw_text.strip()
        if not normalized_text:
            raise AudioTranscriptionError("Provider OpenAI retornou transcricao vazia.")

        return AudioTranscription(text=normalized_text, provider="openai", model=self._model)


def build_audio_transcriber(*, client: Any | None = None) -> AudioTranscriber:
    """Monta provider de transcricao com base na configuracao do ambiente."""
    provider = settings.audio_transcription_provider.strip().lower()
    if provider == "openai":
        return OpenAIAudioTranscriber(
            model=settings.audio_transcription_model,
            language=settings.audio_transcription_language,
            client=client,
        )
    
    if provider == "groq":
        groq_base_url = "https://api.groq.com/openai/v1"
        groq_model = settings.audio_transcription_model if settings.audio_transcription_model != "whisper-1" else "whisper-large-v3"
        return OpenAIAudioTranscriber(
            model=groq_model,
            language=settings.audio_transcription_language,
            client=client,
            api_key=settings.groq_api_key,
            base_url=groq_base_url,
        )

    raise UnsupportedAudioTranscriptionProviderError(
        "Provider de transcricao nao suportado: "
        f"{settings.audio_transcription_provider}. Suportados atualmente: openai, groq."
    )


async def transcribe_audio_event(
    event: NormalizedIncomingEvent,
    *,
    transcriber: AudioTranscriber | None = None,
    downloader: AudioDownloader | None = None,
) -> AudioTranscription:
    """Executa fluxo de transcricao de audio a partir do evento normalizado."""
    audio_attachment = _select_audio_attachment(event.attachments)
    if audio_attachment is None:
        raise AudioAttachmentNotFoundError("Evento nao contem anexo de audio para transcricao.")

    if audio_attachment.public_url is None:
        raise AudioAttachmentNotFoundError("Anexo de audio sem `public_url`, impossivel transcrever.")

    effective_downloader = downloader or _download_audio_file
    try:
        audio_bytes = await effective_downloader(audio_attachment.public_url)
    except AudioDownloadError:
        raise
    except Exception as exc:  # pragma: no cover
        raise AudioDownloadError("Falha inesperada ao baixar arquivo de audio para transcricao.") from exc

    effective_transcriber = transcriber or build_audio_transcriber()
    return await effective_transcriber.transcribe(
        audio_bytes=audio_bytes,
        mime_type=audio_attachment.mime_type,
        file_name=audio_attachment.file_name,
    )


async def _download_audio_file(url: str) -> bytes:
    """Baixa arquivo de audio para transcricao com timeout configuravel."""
    try:
        async with httpx.AsyncClient(timeout=settings.audio_download_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise AudioDownloadError(f"Falha ao baixar audio: status={exc.response.status_code} url={url}") from exc
    except httpx.RequestError as exc:
        raise AudioDownloadError(f"Falha de rede ao baixar audio: url={url}") from exc

    if not response.content:
        raise AudioDownloadError(f"Arquivo de audio vazio recebido da URL: {url}")

    return response.content


def _select_audio_attachment(attachments: list[NormalizedAttachment]) -> NormalizedAttachment | None:
    for attachment in attachments:
        if attachment.mime_type.lower().startswith("audio/"):
            return attachment

    return None
