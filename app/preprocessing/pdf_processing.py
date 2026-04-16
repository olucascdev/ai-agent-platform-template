"""Processamento de PDF com provider configuravel para o preprocessor."""

import importlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Protocol

import httpx

from app.config import settings
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent

PdfDownloader = Callable[[str], Awaitable[bytes]]
PdfReaderFactory = Callable[[bytes], Any]


class PdfProcessingError(RuntimeError):
    """Erro base para falhas de processamento de PDF."""


class UnsupportedPdfProcessingProviderError(PdfProcessingError):
    """Erro quando provider configurado de PDF nao e suportado."""


class PdfAttachmentNotFoundError(PdfProcessingError):
    """Erro quando evento nao contem anexo de PDF valido."""


class PdfDownloadError(PdfProcessingError):
    """Erro ao baixar arquivo PDF para processamento."""


@dataclass(frozen=True, slots=True)
class PdfProcessing:
    """Resultado do processamento textual de PDF."""

    text: str
    provider: str
    pages_processed: int


class PdfProcessor(Protocol):
    """Contrato de provider de processamento de PDF."""

    async def process(self, *, pdf_bytes: bytes, file_name: str | None) -> PdfProcessing:
        """Retorna texto extraido do PDF."""


class PyPdfProcessor:
    """Processador de PDF usando biblioteca pypdf."""

    def __init__(self, *, max_pages: int, reader_factory: PdfReaderFactory | None = None) -> None:
        self._max_pages = max_pages
        self._reader_factory = reader_factory or _build_default_pypdf_reader

    async def process(self, *, pdf_bytes: bytes, file_name: str | None) -> PdfProcessing:
        """Extrai texto de PDF com limite de paginas configuravel."""
        if not pdf_bytes:
            raise PdfProcessingError("Arquivo PDF vazio recebido para processamento.")

        try:
            reader = self._reader_factory(pdf_bytes)
        except Exception as exc:
            raise PdfProcessingError("Falha ao abrir PDF com provider pypdf.") from exc

        pages = getattr(reader, "pages", None)
        if not isinstance(pages, list):
            try:
                pages = list(pages) if pages is not None else []
            except Exception as exc:
                raise PdfProcessingError("Provider pypdf retornou estrutura de paginas invalida.") from exc

        extracted_chunks: list[str] = []
        pages_processed = 0
        for page in pages[: self._max_pages]:
            pages_processed += 1
            text = _extract_text_from_page(page)
            if text:
                extracted_chunks.append(text)

        normalized_text = "\n\n".join(extracted_chunks).strip()
        if not normalized_text:
            file_label = (file_name or "arquivo.pdf").strip() or "arquivo.pdf"
            raise PdfProcessingError(f"Nao foi possivel extrair texto do PDF informado: {file_label}.")

        return PdfProcessing(text=normalized_text, provider="pypdf", pages_processed=pages_processed)


def build_pdf_processor(*, reader_factory: PdfReaderFactory | None = None) -> PdfProcessor:
    """Monta provider de processamento de PDF com base na configuracao."""
    provider = settings.pdf_processing_provider.strip().lower()
    if provider == "pypdf":
        return PyPdfProcessor(max_pages=settings.pdf_processing_max_pages, reader_factory=reader_factory)

    raise UnsupportedPdfProcessingProviderError(
        f"Provider de processamento de PDF nao suportado: {settings.pdf_processing_provider}."
    )


async def process_pdf_event(
    event: NormalizedIncomingEvent,
    *,
    processor: PdfProcessor | None = None,
    downloader: PdfDownloader | None = None,
) -> PdfProcessing:
    """Executa fluxo de processamento de PDF a partir do evento normalizado."""
    pdf_attachment = _select_pdf_attachment(event.attachments)
    if pdf_attachment is None:
        raise PdfAttachmentNotFoundError("Evento nao contem anexo PDF para processamento.")

    if pdf_attachment.public_url is None:
        raise PdfAttachmentNotFoundError("Anexo PDF sem `public_url`, impossivel processar.")

    effective_downloader = downloader or _download_pdf_file
    try:
        pdf_bytes = await effective_downloader(pdf_attachment.public_url)
    except PdfDownloadError:
        raise
    except Exception as exc:  # pragma: no cover
        raise PdfDownloadError("Falha inesperada ao baixar PDF para processamento.") from exc

    effective_processor = processor or build_pdf_processor()
    return await effective_processor.process(pdf_bytes=pdf_bytes, file_name=pdf_attachment.file_name)


async def _download_pdf_file(url: str) -> bytes:
    """Baixa arquivo PDF para processamento com timeout configuravel."""
    try:
        async with httpx.AsyncClient(timeout=settings.pdf_download_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise PdfDownloadError(f"Falha ao baixar PDF: status={exc.response.status_code} url={url}") from exc
    except httpx.RequestError as exc:
        raise PdfDownloadError(f"Falha de rede ao baixar PDF: url={url}") from exc

    if not response.content:
        raise PdfDownloadError(f"Arquivo PDF vazio recebido da URL: {url}")

    return response.content


def _select_pdf_attachment(attachments: list[NormalizedAttachment]) -> NormalizedAttachment | None:
    for attachment in attachments:
        mime_type = attachment.mime_type.lower().split(";", maxsplit=1)[0].strip()
        if mime_type == "application/pdf":
            return attachment

    return None


def _extract_text_from_page(page: Any) -> str:
    extract_method = getattr(page, "extract_text", None)
    if not callable(extract_method):
        return ""

    extracted = extract_method()
    if not isinstance(extracted, str):
        return ""

    return extracted.strip()


def _build_default_pypdf_reader(pdf_bytes: bytes) -> Any:
    try:
        pypdf_module = importlib.import_module("pypdf")
    except Exception as exc:
        raise UnsupportedPdfProcessingProviderError(
            "Biblioteca pypdf nao disponivel para processamento de PDF."
        ) from exc

    return pypdf_module.PdfReader(BytesIO(pdf_bytes))
