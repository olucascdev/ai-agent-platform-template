"""Testes da feature 5.2 de transcricao de audio configuravel."""

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.config import settings
from app.preprocessing import (
    AudioAttachmentNotFoundError,
    AudioDownloadError,
    AudioTranscription,
    AudioTranscriptionError,
    OpenAIAudioTranscriber,
    UnsupportedAudioTranscriptionProviderError,
    build_audio_transcriber,
    transcribe_audio_event,
)
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent


def _build_event(*, attachments: list[NormalizedAttachment]) -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sessao-1",
        contact_phone="+5531999999999",
        input_type="audio",
        text=None,
        attachments=attachments,
        message_id="msg-1",
        message_created_at="2026-04-16T12:00:00Z",
        message_type_raw="AUDIO",
        contact_name="Joel",
        channel_platform="WhatsApp",
    )


@dataclass
class _FakeTranscriber:
    captured_audio_bytes: bytes | None = None
    captured_mime_type: str | None = None
    captured_file_name: str | None = None

    async def transcribe(self, *, audio_bytes: bytes, mime_type: str, file_name: str | None) -> AudioTranscription:
        self.captured_audio_bytes = audio_bytes
        self.captured_mime_type = mime_type
        self.captured_file_name = file_name
        return AudioTranscription(text="texto transcrito", provider="fake", model="fake-1")


@pytest.mark.asyncio
async def test_transcribe_audio_event_happy_path_with_injected_dependencies() -> None:
    """Transcreve audio com downloader/provider injetados no fluxo principal."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="file-a1",
            )
        ]
    )

    fake_transcriber = _FakeTranscriber()

    async def fake_downloader(url: str) -> bytes:
        assert url == "https://cdn.exemplo.com/audio.ogg"
        return b"audio-bytes"

    result = await transcribe_audio_event(event, transcriber=fake_transcriber, downloader=fake_downloader)

    assert result.text == "texto transcrito"
    assert fake_transcriber.captured_audio_bytes == b"audio-bytes"
    assert fake_transcriber.captured_mime_type == "audio/ogg"
    assert fake_transcriber.captured_file_name == "audio.ogg"


@pytest.mark.asyncio
async def test_transcribe_audio_event_raises_when_no_audio_attachment_exists() -> None:
    """Falha quando evento nao possui anexo de audio valido."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="image/png",
                public_url="https://cdn.exemplo.com/imagem.png",
                file_name="imagem.png",
                file_id="img-1",
            )
        ]
    )

    async def fake_downloader(_url: str) -> bytes:
        return b"x"

    with pytest.raises(AudioAttachmentNotFoundError) as exc_info:
        await transcribe_audio_event(event, transcriber=_FakeTranscriber(), downloader=fake_downloader)

    assert "nao contem anexo de audio" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_transcribe_audio_event_raises_when_audio_has_no_public_url() -> None:
    """Falha quando anexo de audio existe mas sem URL de download."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="audio/mpeg",
                public_url=None,
                file_name="audio.mp3",
                file_id="a-2",
            )
        ]
    )

    async def fake_downloader(_url: str) -> bytes:
        return b"x"

    with pytest.raises(AudioAttachmentNotFoundError) as exc_info:
        await transcribe_audio_event(event, transcriber=_FakeTranscriber(), downloader=fake_downloader)

    assert "public_url" in str(exc_info.value)


@pytest.mark.asyncio
async def test_transcribe_audio_event_wraps_unexpected_download_failure() -> None:
    """Converte erro inesperado do downloader para erro de dominio da feature."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="a-3",
            )
        ]
    )

    async def broken_downloader(_url: str) -> bytes:
        raise RuntimeError("falha inesperada")

    with pytest.raises(AudioDownloadError) as exc_info:
        await transcribe_audio_event(event, transcriber=_FakeTranscriber(), downloader=broken_downloader)

    assert "falha inesperada" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_openai_transcriber_sends_expected_payload_to_client() -> None:
    """Valida contrato de chamada OpenAI sem depender de API externa."""

    class _FakeTranscriptions:
        def __init__(self) -> None:
            self.last_kwargs: dict[str, object] = {}

        async def create(self, **kwargs: object) -> object:
            self.last_kwargs = kwargs
            return SimpleNamespace(text="  texto final  ")

    fake_transcriptions = _FakeTranscriptions()
    fake_client = SimpleNamespace(audio=SimpleNamespace(transcriptions=fake_transcriptions))
    transcriber = OpenAIAudioTranscriber(model="whisper-1", language="pt", client=fake_client)

    result = await transcriber.transcribe(
        audio_bytes=b"audio-content",
        mime_type="audio/ogg",
        file_name="arquivo.ogg",
    )

    assert result.text == "texto final"
    assert result.provider == "openai"
    assert result.model == "whisper-1"
    assert fake_transcriptions.last_kwargs["model"] == "whisper-1"
    assert fake_transcriptions.last_kwargs["language"] == "pt"


@pytest.mark.asyncio
async def test_openai_transcriber_raises_when_provider_returns_empty_text() -> None:
    """Falha quando provider retorna transcricao vazia."""

    class _FakeTranscriptions:
        async def create(self, **_kwargs: object) -> object:
            return SimpleNamespace(text="   ")

    fake_client = SimpleNamespace(audio=SimpleNamespace(transcriptions=_FakeTranscriptions()))
    transcriber = OpenAIAudioTranscriber(model="whisper-1", client=fake_client)

    with pytest.raises(AudioTranscriptionError) as exc_info:
        await transcriber.transcribe(audio_bytes=b"audio", mime_type="audio/ogg", file_name="a.ogg")

    assert "transcricao vazia" in str(exc_info.value).lower()


def test_build_audio_transcriber_uses_openai_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monta provider OpenAI quando configuracao padrao esta ativa."""
    monkeypatch.setattr(settings, "audio_transcription_provider", "openai")
    monkeypatch.setattr(settings, "audio_transcription_model", "whisper-1")
    monkeypatch.setattr(settings, "audio_transcription_language", None)

    transcriber = build_audio_transcriber(client=SimpleNamespace(audio=SimpleNamespace(transcriptions=None)))

    assert isinstance(transcriber, OpenAIAudioTranscriber)


def test_build_audio_transcriber_raises_for_unsupported_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha explicitamente para provider nao suportado na configuracao."""
    monkeypatch.setattr(settings, "audio_transcription_provider", "desconhecido")

    with pytest.raises(UnsupportedAudioTranscriptionProviderError) as exc_info:
        build_audio_transcriber(client=SimpleNamespace(audio=SimpleNamespace(transcriptions=None)))

    assert "nao suportado" in str(exc_info.value).lower()
