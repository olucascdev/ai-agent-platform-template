"""Composicao final de contexto para consumo do agente conversacional."""

from dataclasses import dataclass
from typing import Literal

from app.preprocessing.audio_transcription import AudioTranscription
from app.preprocessing.event_normalizer import NormalizedIncomingEvent
from app.preprocessing.image_analysis import ImageAnalysis
from app.preprocessing.pdf_processing import PdfProcessing

ComposerSource = Literal["text", "audio_transcription", "image_analysis", "pdf_processing"]
SOURCE_PRIORITY: tuple[ComposerSource, ...] = (
    "text",
    "audio_transcription",
    "image_analysis",
    "pdf_processing",
)


class MessageCompositionError(RuntimeError):
    """Erro quando nao existe conteudo textual suficiente para compor entrada do agente."""


@dataclass(frozen=True, slots=True)
class ComposedAgentInput:
    """Representa resultado final da composicao textual para o agente."""

    primary_source: ComposerSource
    primary_text: str
    supplemental_sources: tuple[ComposerSource, ...]
    source_texts: dict[ComposerSource, str]
    message_for_agent: str


def compose_agent_input(
    *,
    event: NormalizedIncomingEvent,
    audio_transcription: AudioTranscription | None = None,
    image_analysis: ImageAnalysis | None = None,
    pdf_processing: PdfProcessing | None = None,
) -> ComposedAgentInput:
    """Compoe mensagem final para o agente com prioridade e merge deterministico."""
    source_texts = _collect_source_texts(
        event=event,
        audio_transcription=audio_transcription,
        image_analysis=image_analysis,
        pdf_processing=pdf_processing,
    )
    if not source_texts:
        raise MessageCompositionError("Nao foi possivel compor entrada para o agente: nenhum texto util encontrado.")

    primary_source = _resolve_primary_source(source_texts)
    primary_text = source_texts[primary_source]
    supplemental_sources = tuple(
        source for source in SOURCE_PRIORITY if source in source_texts and source != primary_source
    )
    message_for_agent = _build_agent_message(
        primary_source=primary_source,
        primary_text=primary_text,
        supplemental_sources=supplemental_sources,
        source_texts=source_texts,
    )

    return ComposedAgentInput(
        primary_source=primary_source,
        primary_text=primary_text,
        supplemental_sources=supplemental_sources,
        source_texts=source_texts,
        message_for_agent=message_for_agent,
    )


def _collect_source_texts(
    *,
    event: NormalizedIncomingEvent,
    audio_transcription: AudioTranscription | None,
    image_analysis: ImageAnalysis | None,
    pdf_processing: PdfProcessing | None,
) -> dict[ComposerSource, str]:
    source_texts: dict[ComposerSource, str] = {}

    event_text = _normalize_text(event.text)
    if event_text is not None:
        source_texts["text"] = event_text

    if audio_transcription is not None:
        audio_text = _normalize_text(audio_transcription.text)
        if audio_text is not None:
            source_texts["audio_transcription"] = audio_text

    if image_analysis is not None:
        image_text = _normalize_text(image_analysis.text)
        if image_text is not None:
            source_texts["image_analysis"] = image_text

    if pdf_processing is not None:
        pdf_text = _normalize_text(pdf_processing.text)
        if pdf_text is not None:
            source_texts["pdf_processing"] = pdf_text

    return source_texts


def _resolve_primary_source(source_texts: dict[ComposerSource, str]) -> ComposerSource:
    for source in SOURCE_PRIORITY:
        if source in source_texts:
            return source

    raise MessageCompositionError("Nao existe fonte valida para definir mensagem principal do agente.")


def _build_agent_message(
    *,
    primary_source: ComposerSource,
    primary_text: str,
    supplemental_sources: tuple[ComposerSource, ...],
    source_texts: dict[ComposerSource, str],
) -> str:
    blocks: list[str] = [
        "[mensagem_principal]",
        f"fonte={primary_source}",
        primary_text,
    ]

    if supplemental_sources:
        blocks.extend(["", "[contexto_complementar]"])
        for source in supplemental_sources:
            blocks.append(f"[{source}]")
            blocks.append(source_texts[source])
            blocks.append("")

        if blocks and blocks[-1] == "":
            blocks.pop()

    return "\n".join(blocks).strip()


def _normalize_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None
