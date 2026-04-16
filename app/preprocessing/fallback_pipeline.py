"""Orquestracao resiliente do preprocessor com fallback seguro para falhas de midia."""

from dataclasses import dataclass
from typing import Literal

from app.config import settings
from app.preprocessing.audio_transcription import (
    AudioDownloader,
    AudioTranscriber,
    AudioTranscription,
    AudioTranscriptionError,
    transcribe_audio_event,
)
from app.preprocessing.event_normalizer import NormalizedIncomingEvent
from app.preprocessing.image_analysis import (
    ImageAnalysis,
    ImageAnalysisError,
    ImageAnalyzer,
    ImageDownloader,
    analyze_image_event,
)
from app.preprocessing.message_composer import ComposedAgentInput, MessageCompositionError, compose_agent_input
from app.preprocessing.pdf_processing import (
    PdfDownloader,
    PdfProcessing,
    PdfProcessingError,
    PdfProcessor,
    process_pdf_event,
)

PreprocessingStage = Literal["audio_transcription", "image_analysis", "pdf_processing", "message_composition"]


@dataclass(frozen=True, slots=True)
class PreprocessingIssue:
    """Representa falha capturada no preprocessamento multimodal."""

    stage: PreprocessingStage
    error_type: str
    message: str


@dataclass(frozen=True, slots=True)
class ResilientPreprocessingResult:
    """Resultado resiliente do pipeline, com ou sem fallback de midia."""

    event: NormalizedIncomingEvent
    composed_input: ComposedAgentInput | None
    message_for_agent: str
    used_fallback_message: bool
    audio_transcription: AudioTranscription | None
    image_analysis: ImageAnalysis | None
    pdf_processing: PdfProcessing | None
    issues: tuple[PreprocessingIssue, ...]


async def preprocess_event_with_fallback(
    event: NormalizedIncomingEvent,
    *,
    transcriber: AudioTranscriber | None = None,
    image_analyzer: ImageAnalyzer | None = None,
    pdf_processor: PdfProcessor | None = None,
    audio_downloader: AudioDownloader | None = None,
    image_downloader: ImageDownloader | None = None,
    pdf_downloader: PdfDownloader | None = None,
    fallback_text: str | None = None,
) -> ResilientPreprocessingResult:
    """Executa preprocessor multimodal sem quebrar o fluxo em falhas de provider."""
    issues: list[PreprocessingIssue] = []

    audio_transcription: AudioTranscription | None = None
    if _event_has_audio(event):
        try:
            audio_transcription = await transcribe_audio_event(
                event,
                transcriber=transcriber,
                downloader=audio_downloader,
            )
        except AudioTranscriptionError as exc:
            issues.append(_build_issue(stage="audio_transcription", exc=exc))
        except Exception as exc:  # pragma: no cover
            issues.append(_build_issue(stage="audio_transcription", exc=exc))

    image_analysis: ImageAnalysis | None = None
    if _event_has_image(event):
        try:
            image_analysis = await analyze_image_event(
                event,
                analyzer=image_analyzer,
                downloader=image_downloader,
            )
        except ImageAnalysisError as exc:
            issues.append(_build_issue(stage="image_analysis", exc=exc))
        except Exception as exc:  # pragma: no cover
            issues.append(_build_issue(stage="image_analysis", exc=exc))

    pdf_processing: PdfProcessing | None = None
    if _event_has_pdf(event):
        try:
            pdf_processing = await process_pdf_event(
                event,
                processor=pdf_processor,
                downloader=pdf_downloader,
            )
        except PdfProcessingError as exc:
            issues.append(_build_issue(stage="pdf_processing", exc=exc))
        except Exception as exc:  # pragma: no cover
            issues.append(_build_issue(stage="pdf_processing", exc=exc))

    composed_input: ComposedAgentInput | None = None
    used_fallback_message = False
    message_for_agent: str
    try:
        composed_input = compose_agent_input(
            event=event,
            audio_transcription=audio_transcription,
            image_analysis=image_analysis,
            pdf_processing=pdf_processing,
        )
        message_for_agent = composed_input.message_for_agent
    except MessageCompositionError as exc:
        issues.append(_build_issue(stage="message_composition", exc=exc))
        used_fallback_message = True
        message_for_agent = _build_fallback_message(
            fallback_text=fallback_text or settings.media_failure_fallback_text,
            issues=tuple(issues),
        )

    return ResilientPreprocessingResult(
        event=event,
        composed_input=composed_input,
        message_for_agent=message_for_agent,
        used_fallback_message=used_fallback_message,
        audio_transcription=audio_transcription,
        image_analysis=image_analysis,
        pdf_processing=pdf_processing,
        issues=tuple(issues),
    )


def _build_issue(*, stage: PreprocessingStage, exc: Exception) -> PreprocessingIssue:
    message = str(exc).strip() or "Falha sem mensagem detalhada."
    return PreprocessingIssue(stage=stage, error_type=exc.__class__.__name__, message=message)


def _event_has_audio(event: NormalizedIncomingEvent) -> bool:
    if event.input_type == "audio":
        return True

    return any(attachment.mime_type.lower().startswith("audio/") for attachment in event.attachments)


def _event_has_image(event: NormalizedIncomingEvent) -> bool:
    if event.input_type == "image":
        return True

    return any(attachment.mime_type.lower().startswith("image/") for attachment in event.attachments)


def _event_has_pdf(event: NormalizedIncomingEvent) -> bool:
    if event.input_type == "pdf":
        return True

    return any(
        attachment.mime_type.lower().split(";", maxsplit=1)[0].strip() == "application/pdf"
        for attachment in event.attachments
    )


def _build_fallback_message(*, fallback_text: str, issues: tuple[PreprocessingIssue, ...]) -> str:
    normalized_fallback = fallback_text.strip() or settings.media_failure_fallback_text
    blocks: list[str] = [
        "[mensagem_principal]",
        "fonte=text",
        normalized_fallback,
    ]

    if issues:
        blocks.extend(["", "[falhas_preprocessamento]"])
        for issue in issues:
            blocks.append(f"[{issue.stage}] {issue.error_type}: {issue.message}")

    return "\n".join(blocks).strip()
