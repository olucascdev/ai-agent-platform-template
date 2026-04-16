"""Testes da feature 5.4 de processamento de PDF."""

from dataclasses import dataclass

import pytest

from app.config import settings
from app.preprocessing import (
    PdfAttachmentNotFoundError,
    PdfDownloadError,
    PdfProcessing,
    PdfProcessingError,
    PyPdfProcessor,
    UnsupportedPdfProcessingProviderError,
    build_pdf_processor,
    process_pdf_event,
)
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent


def _build_event(*, attachments: list[NormalizedAttachment], text: str | None = None) -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sessao-1",
        contact_phone="+5531999999999",
        input_type="pdf",
        text=text,
        attachments=attachments,
        message_id="msg-1",
        message_created_at="2026-04-16T12:00:00Z",
        message_type_raw="DOCUMENT",
        contact_name="Joel",
        channel_platform="WhatsApp",
    )


@dataclass
class _FakePdfProcessor:
    captured_pdf_bytes: bytes | None = None
    captured_file_name: str | None = None

    async def process(self, *, pdf_bytes: bytes, file_name: str | None) -> PdfProcessing:
        self.captured_pdf_bytes = pdf_bytes
        self.captured_file_name = file_name
        return PdfProcessing(text="texto do pdf", provider="fake", pages_processed=1)


@pytest.mark.asyncio
async def test_process_pdf_event_happy_path_with_injected_dependencies() -> None:
    """Processa PDF com downloader/provider injetados no fluxo principal."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="application/pdf",
                public_url="https://cdn.exemplo.com/arquivo.pdf",
                file_name="arquivo.pdf",
                file_id="pdf-1",
            )
        ]
    )

    fake_processor = _FakePdfProcessor()

    async def fake_downloader(url: str) -> bytes:
        assert url == "https://cdn.exemplo.com/arquivo.pdf"
        return b"pdf-bytes"

    result = await process_pdf_event(event, processor=fake_processor, downloader=fake_downloader)

    assert result.text == "texto do pdf"
    assert fake_processor.captured_pdf_bytes == b"pdf-bytes"
    assert fake_processor.captured_file_name == "arquivo.pdf"


@pytest.mark.asyncio
async def test_process_pdf_event_raises_when_no_pdf_attachment_exists() -> None:
    """Falha quando evento nao possui anexo PDF."""
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

    with pytest.raises(PdfAttachmentNotFoundError) as exc_info:
        await process_pdf_event(event, processor=_FakePdfProcessor(), downloader=fake_downloader)

    assert "nao contem anexo pdf" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_process_pdf_event_raises_when_pdf_has_no_public_url() -> None:
    """Falha quando anexo PDF existe mas sem URL de download."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="application/pdf",
                public_url=None,
                file_name="arquivo.pdf",
                file_id="pdf-2",
            )
        ]
    )

    async def fake_downloader(_url: str) -> bytes:
        return b"x"

    with pytest.raises(PdfAttachmentNotFoundError) as exc_info:
        await process_pdf_event(event, processor=_FakePdfProcessor(), downloader=fake_downloader)

    assert "public_url" in str(exc_info.value)


@pytest.mark.asyncio
async def test_process_pdf_event_wraps_unexpected_download_failure() -> None:
    """Converte erro inesperado no downloader para erro de dominio da feature."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="application/pdf;charset=utf-8",
                public_url="https://cdn.exemplo.com/arquivo.pdf",
                file_name="arquivo.pdf",
                file_id="pdf-3",
            )
        ]
    )

    async def broken_downloader(_url: str) -> bytes:
        raise RuntimeError("falha inesperada")

    with pytest.raises(PdfDownloadError) as exc_info:
        await process_pdf_event(event, processor=_FakePdfProcessor(), downloader=broken_downloader)

    assert "falha inesperada" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_pypdf_processor_extracts_text_and_respects_max_pages() -> None:
    """Extrai texto com pypdf e respeita limite de paginas configurado."""

    class _FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class _FakeReader:
        def __init__(self) -> None:
            self.pages = [_FakePage("pagina 1"), _FakePage("pagina 2"), _FakePage("pagina 3")]

    processor = PyPdfProcessor(max_pages=2, reader_factory=lambda _bytes: _FakeReader())
    result = await processor.process(pdf_bytes=b"pdf-bytes", file_name="arquivo.pdf")

    assert result.text == "pagina 1\n\npagina 2"
    assert result.provider == "pypdf"
    assert result.pages_processed == 2


@pytest.mark.asyncio
async def test_pypdf_processor_raises_when_no_text_is_extracted() -> None:
    """Falha com erro explicito quando PDF nao gera texto util."""

    class _FakePage:
        def extract_text(self) -> str:
            return "   "

    class _FakeReader:
        def __init__(self) -> None:
            self.pages = [_FakePage()]

    processor = PyPdfProcessor(max_pages=5, reader_factory=lambda _bytes: _FakeReader())

    with pytest.raises(PdfProcessingError) as exc_info:
        await processor.process(pdf_bytes=b"pdf-bytes", file_name="arquivo.pdf")

    assert "nao foi possivel extrair texto" in str(exc_info.value).lower()


def test_build_pdf_processor_uses_pypdf_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monta provider pypdf quando configuracao padrao esta ativa."""
    monkeypatch.setattr(settings, "pdf_processing_provider", "pypdf")
    monkeypatch.setattr(settings, "pdf_processing_max_pages", 15)

    processor = build_pdf_processor(reader_factory=lambda _bytes: object())

    assert isinstance(processor, PyPdfProcessor)


def test_build_pdf_processor_raises_for_unsupported_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha explicitamente para provider de PDF nao suportado."""
    monkeypatch.setattr(settings, "pdf_processing_provider", "desconhecido")

    with pytest.raises(UnsupportedPdfProcessingProviderError) as exc_info:
        build_pdf_processor(reader_factory=lambda _bytes: object())

    assert "nao suportado" in str(exc_info.value).lower()
