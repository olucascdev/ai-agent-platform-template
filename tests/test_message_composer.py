"""Testes da feature 5.5 de composicao final de contexto para o agente."""

import pytest

from app.preprocessing import (
    AudioTranscription,
    ImageAnalysis,
    MessageCompositionError,
    PdfProcessing,
    compose_agent_input,
)
from app.preprocessing.event_normalizer import NormalizedIncomingEvent


def _build_event(*, text: str | None) -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sessao-1",
        contact_phone="+5531999999999",
        input_type="text",
        text=text,
        attachments=[],
        message_id="msg-1",
        message_created_at="2026-04-16T12:00:00Z",
        message_type_raw="TEXT",
        contact_name="Joel",
        channel_platform="WhatsApp",
    )


def test_message_composer_prioritizes_event_text_over_other_sources() -> None:
    """Usa texto direto do evento como fonte principal quando disponivel."""
    composed = compose_agent_input(
        event=_build_event(text="Quero falar com comercial"),
        audio_transcription=AudioTranscription(text="audio alternativo", provider="openai", model="whisper-1"),
        image_analysis=ImageAnalysis(text="imagem com texto", provider="google", model="gemini"),
        pdf_processing=PdfProcessing(text="conteudo PDF", provider="pypdf", pages_processed=2),
    )

    assert composed.primary_source == "text"
    assert composed.primary_text == "Quero falar com comercial"
    assert composed.supplemental_sources == (
        "audio_transcription",
        "image_analysis",
        "pdf_processing",
    )
    assert "fonte=text" in composed.message_for_agent
    assert "[audio_transcription]" in composed.message_for_agent


def test_message_composer_falls_back_to_audio_when_text_is_missing() -> None:
    """Seleciona transcricao de audio quando texto do evento nao existe."""
    composed = compose_agent_input(
        event=_build_event(text=None),
        audio_transcription=AudioTranscription(text="texto vindo do audio", provider="openai", model="whisper-1"),
        image_analysis=ImageAnalysis(text="texto da imagem", provider="google", model="gemini"),
    )

    assert composed.primary_source == "audio_transcription"
    assert composed.primary_text == "texto vindo do audio"
    assert composed.supplemental_sources == ("image_analysis",)


def test_message_composer_prefers_image_before_pdf_when_no_text_or_audio() -> None:
    """Respeita prioridade imagem > pdf quando texto/audio nao existem."""
    composed = compose_agent_input(
        event=_build_event(text=None),
        image_analysis=ImageAnalysis(text="resultado da imagem", provider="google", model="gemini"),
        pdf_processing=PdfProcessing(text="resultado do pdf", provider="pypdf", pages_processed=1),
    )

    assert composed.primary_source == "image_analysis"
    assert composed.supplemental_sources == ("pdf_processing",)


def test_message_composer_uses_pdf_as_last_textual_fallback() -> None:
    """Usa PDF como fallback final quando nenhuma outra fonte textual existe."""
    composed = compose_agent_input(
        event=_build_event(text=None),
        pdf_processing=PdfProcessing(text="somente pdf disponivel", provider="pypdf", pages_processed=3),
    )

    assert composed.primary_source == "pdf_processing"
    assert composed.primary_text == "somente pdf disponivel"
    assert composed.supplemental_sources == ()


def test_message_composer_ignores_empty_texts_from_sources() -> None:
    """Ignora fontes com texto vazio e mantem composicao deterministica."""
    composed = compose_agent_input(
        event=_build_event(text="   "),
        audio_transcription=AudioTranscription(text="  texto audio  ", provider="openai", model="whisper-1"),
        image_analysis=ImageAnalysis(text="   ", provider="google", model="gemini"),
        pdf_processing=PdfProcessing(text="  texto pdf  ", provider="pypdf", pages_processed=1),
    )

    assert composed.primary_source == "audio_transcription"
    assert composed.source_texts == {
        "audio_transcription": "texto audio",
        "pdf_processing": "texto pdf",
    }
    assert composed.supplemental_sources == ("pdf_processing",)


def test_message_composer_raises_when_no_textual_content_exists() -> None:
    """Falha explicitamente quando nenhuma fonte textual util esta disponivel."""
    with pytest.raises(MessageCompositionError) as exc_info:
        compose_agent_input(event=_build_event(text="   "))

    assert "nenhum texto util" in str(exc_info.value).lower()


def test_message_composer_generates_deterministic_output() -> None:
    """Garante resultado identico para a mesma entrada de composicao."""
    event = _build_event(text="mensagem principal")
    audio = AudioTranscription(text="audio", provider="openai", model="whisper-1")
    image = ImageAnalysis(text="imagem", provider="google", model="gemini")
    pdf = PdfProcessing(text="pdf", provider="pypdf", pages_processed=1)

    first = compose_agent_input(
        event=event,
        audio_transcription=audio,
        image_analysis=image,
        pdf_processing=pdf,
    )
    second = compose_agent_input(
        event=event,
        audio_transcription=audio,
        image_analysis=image,
        pdf_processing=pdf,
    )

    assert first.message_for_agent == second.message_for_agent
    assert first.supplemental_sources == second.supplemental_sources
