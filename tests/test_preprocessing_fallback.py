"""Testes da feature 5.6 de fallback seguro no pipeline de preprocessamento."""

from dataclasses import dataclass

import pytest

from app.preprocessing import (
    AudioTranscription,
    AudioTranscriptionError,
    ImageAnalysis,
    PdfProcessing,
    PdfProcessingError,
    preprocess_event_with_fallback,
)
from app.preprocessing.event_normalizer import InputType, NormalizedAttachment, NormalizedIncomingEvent


def _build_event(
    *,
    input_type: InputType,
    text: str | None,
    attachments: list[NormalizedAttachment],
) -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sessao-1",
        contact_phone="+5531999999999",
        input_type=input_type,
        text=text,
        attachments=attachments,
        message_id="msg-1",
        message_created_at="2026-04-16T12:00:00Z",
        message_type_raw="TEXT",
        contact_name="Joel",
        channel_platform="WhatsApp",
    )


@dataclass
class _OkAudioTranscriber:
    async def transcribe(self, *, audio_bytes: bytes, mime_type: str, file_name: str | None) -> AudioTranscription:
        return AudioTranscription(text="texto do audio", provider="fake", model="fake-audio")


@dataclass
class _FailAudioTranscriber:
    async def transcribe(self, *, audio_bytes: bytes, mime_type: str, file_name: str | None) -> AudioTranscription:
        raise AudioTranscriptionError("provider de audio indisponivel")


@dataclass
class _OkImageAnalyzer:
    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        file_name: str | None,
        text_hint: str | None,
    ) -> ImageAnalysis:
        return ImageAnalysis(text="texto da imagem", provider="fake", model="fake-image")


@dataclass
class _FailPdfProcessor:
    async def process(self, *, pdf_bytes: bytes, file_name: str | None) -> PdfProcessing:
        raise PdfProcessingError("falha ao processar pdf")


@dataclass
class _OkPdfProcessor:
    async def process(self, *, pdf_bytes: bytes, file_name: str | None) -> PdfProcessing:
        return PdfProcessing(text="texto do pdf", provider="fake", pages_processed=1)


@pytest.mark.asyncio
async def test_preprocess_fallback_keeps_regular_composition_when_text_exists() -> None:
    """Mantem composicao normal sem fallback para evento textual valido."""
    event = _build_event(input_type="text", text="Preciso de ajuda", attachments=[])

    result = await preprocess_event_with_fallback(event)

    assert result.used_fallback_message is False
    assert result.composed_input is not None
    assert result.composed_input.primary_source == "text"
    assert result.issues == ()


@pytest.mark.asyncio
async def test_preprocess_fallback_records_audio_failure_and_uses_text_when_available() -> None:
    """Registra erro de audio sem quebrar fluxo quando texto principal existe."""
    event = _build_event(
        input_type="audio",
        text="Mensagem digitada pelo usuario",
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="a-1",
            )
        ],
    )

    async def fake_audio_downloader(_url: str) -> bytes:
        return b"audio-bytes"

    result = await preprocess_event_with_fallback(
        event,
        transcriber=_FailAudioTranscriber(),
        audio_downloader=fake_audio_downloader,
    )

    assert result.used_fallback_message is False
    assert result.composed_input is not None
    assert result.composed_input.primary_source == "text"
    assert len(result.issues) == 1
    assert result.issues[0].stage == "audio_transcription"


@pytest.mark.asyncio
async def test_preprocess_fallback_uses_safe_message_when_only_media_fails() -> None:
    """Usa fallback seguro quando nao existe texto util apos falha de midia."""
    event = _build_event(
        input_type="audio",
        text=None,
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="a-2",
            )
        ],
    )

    async def fake_audio_downloader(_url: str) -> bytes:
        return b"audio-bytes"

    result = await preprocess_event_with_fallback(
        event,
        transcriber=_FailAudioTranscriber(),
        audio_downloader=fake_audio_downloader,
        fallback_text="Fallback customizado para falha de midia.",
    )

    assert result.used_fallback_message is True
    assert result.composed_input is None
    assert "Fallback customizado para falha de midia." in result.message_for_agent
    stages = tuple(issue.stage for issue in result.issues)
    assert stages == ("audio_transcription", "message_composition")


@pytest.mark.asyncio
async def test_preprocess_fallback_uses_surviving_source_when_pdf_fails() -> None:
    """Mantem imagem como fonte principal quando PDF falha no mesmo evento."""
    event = _build_event(
        input_type="other",
        text=None,
        attachments=[
            NormalizedAttachment(
                mime_type="image/png",
                public_url="https://cdn.exemplo.com/img.png",
                file_name="img.png",
                file_id="img-1",
            ),
            NormalizedAttachment(
                mime_type="application/pdf",
                public_url="https://cdn.exemplo.com/doc.pdf",
                file_name="doc.pdf",
                file_id="pdf-1",
            ),
        ],
    )

    async def fake_image_downloader(_url: str) -> bytes:
        return b"image-bytes"

    async def fake_pdf_downloader(_url: str) -> bytes:
        return b"pdf-bytes"

    result = await preprocess_event_with_fallback(
        event,
        image_analyzer=_OkImageAnalyzer(),
        image_downloader=fake_image_downloader,
        pdf_processor=_FailPdfProcessor(),
        pdf_downloader=fake_pdf_downloader,
    )

    assert result.used_fallback_message is False
    assert result.composed_input is not None
    assert result.composed_input.primary_source == "image_analysis"
    assert len(result.issues) == 1
    assert result.issues[0].stage == "pdf_processing"


@pytest.mark.asyncio
async def test_preprocess_fallback_tracks_successful_media_results() -> None:
    """Retorna artefatos multimodais de sucesso quando providers concluem sem falha."""
    event = _build_event(
        input_type="other",
        text=None,
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="a-3",
            ),
            NormalizedAttachment(
                mime_type="application/pdf",
                public_url="https://cdn.exemplo.com/doc.pdf",
                file_name="doc.pdf",
                file_id="pdf-2",
            ),
        ],
    )

    async def fake_audio_downloader(_url: str) -> bytes:
        return b"audio-bytes"

    async def fake_pdf_downloader(_url: str) -> bytes:
        return b"pdf-bytes"

    result = await preprocess_event_with_fallback(
        event,
        transcriber=_OkAudioTranscriber(),
        audio_downloader=fake_audio_downloader,
        pdf_processor=_OkPdfProcessor(),
        pdf_downloader=fake_pdf_downloader,
    )

    assert result.used_fallback_message is False
    assert result.audio_transcription is not None
    assert result.pdf_processing is not None
    assert result.composed_input is not None
    assert result.composed_input.primary_source == "audio_transcription"
    assert result.composed_input.supplemental_sources == ("pdf_processing",)
