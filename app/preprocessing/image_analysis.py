"""Analise de imagem com provider configuravel para o preprocessor."""

import asyncio
import importlib
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from app.config import settings
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent

ImageDownloader = Callable[[str], Awaitable[bytes]]


class ImageAnalysisError(RuntimeError):
    """Erro base para falhas de analise de imagem."""


class UnsupportedImageAnalysisProviderError(ImageAnalysisError):
    """Erro quando provider configurado de imagem nao e suportado."""


class ImageAttachmentNotFoundError(ImageAnalysisError):
    """Erro quando evento nao contem anexo de imagem valido."""


class ImageDownloadError(ImageAnalysisError):
    """Erro ao baixar arquivo de imagem para analise."""


@dataclass(frozen=True, slots=True)
class ImageAnalysis:
    """Resultado da analise de imagem com metadados do provider."""

    text: str
    provider: str
    model: str


class ImageAnalyzer(Protocol):
    """Contrato de provider de analise de imagem."""

    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        file_name: str | None,
        text_hint: str | None,
    ) -> ImageAnalysis:
        """Retorna analise textual a partir dos bytes da imagem."""


class GoogleImageAnalyzer:
    """Implementacao de analise de imagem usando Google Gemini."""

    def __init__(
        self,
        *,
        model: str,
        prompt: str,
        api_key: str,
        model_client: Any | None = None,
    ) -> None:
        self._model = model
        self._prompt = prompt.strip()
        self._api_key = api_key
        self._model_client = model_client or self._build_default_model_client(model=model, api_key=api_key)

    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        file_name: str | None,
        text_hint: str | None,
    ) -> ImageAnalysis:
        """Executa analise de imagem no provider Google e retorna texto consolidado."""
        if not image_bytes:
            raise ImageAnalysisError("Arquivo de imagem vazio recebido para analise.")

        prompt = self._build_prompt(text_hint=text_hint)
        payload = [prompt, {"inline_data": {"mime_type": mime_type, "data": image_bytes}}]

        try:
            response = await asyncio.to_thread(self._model_client.generate_content, payload)
        except Exception as exc:
            raise ImageAnalysisError("Falha ao executar analise de imagem no provider Google.") from exc

        normalized_text = self._extract_response_text(response)
        if normalized_text is None:
            raise ImageAnalysisError("Provider Google retornou analise vazia para a imagem enviada.")

        return ImageAnalysis(text=normalized_text, provider="google", model=self._model)

    def _build_prompt(self, *, text_hint: str | None) -> str:
        if not text_hint:
            return self._prompt

        return f"{self._prompt}\n\nContexto adicional enviado pelo usuario: {text_hint}"

    @staticmethod
    def _build_default_model_client(*, model: str, api_key: str) -> Any:
        try:
            google_genai = importlib.import_module("google.generativeai")
        except Exception as exc:
            raise UnsupportedImageAnalysisProviderError(
                "Biblioteca do provider Google nao disponivel para analise de imagem."
            ) from exc

        google_genai.configure(api_key=api_key)
        return google_genai.GenerativeModel(model_name=model)

    def _extract_response_text(self, response: Any) -> str | None:
        text_attr = getattr(response, "text", None)
        if isinstance(text_attr, str):
            normalized = text_attr.strip()
            if normalized:
                return normalized

        candidates = getattr(response, "candidates", None)
        if not isinstance(candidates, list):
            return None

        extracted_parts: list[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None)
            if not isinstance(parts, list):
                continue

            for part in parts:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str):
                    normalized = part_text.strip()
                    if normalized:
                        extracted_parts.append(normalized)

        if not extracted_parts:
            return None

        return "\n".join(extracted_parts)


def build_image_analyzer(*, model_client: Any | None = None) -> ImageAnalyzer:
    """Monta provider de analise de imagem com base nas configuracoes."""
    provider = settings.image_analysis_provider.strip().lower()
    if provider == "google":
        return GoogleImageAnalyzer(
            model=settings.image_analysis_model,
            prompt=settings.image_analysis_prompt,
            api_key=settings.google_api_key,
            model_client=model_client,
        )

    raise UnsupportedImageAnalysisProviderError(
        f"Provider de analise de imagem nao suportado: {settings.image_analysis_provider}."
    )


async def analyze_image_event(
    event: NormalizedIncomingEvent,
    *,
    analyzer: ImageAnalyzer | None = None,
    downloader: ImageDownloader | None = None,
) -> ImageAnalysis:
    """Executa fluxo de analise de imagem a partir do evento normalizado."""
    image_attachment = _select_image_attachment(event.attachments)
    if image_attachment is None:
        raise ImageAttachmentNotFoundError("Evento nao contem anexo de imagem para analise.")

    if image_attachment.public_url is None:
        raise ImageAttachmentNotFoundError("Anexo de imagem sem `public_url`, impossivel analisar.")

    effective_downloader = downloader or _download_image_file
    try:
        image_bytes = await effective_downloader(image_attachment.public_url)
    except ImageDownloadError:
        raise
    except Exception as exc:  # pragma: no cover
        raise ImageDownloadError("Falha inesperada ao baixar imagem para analise.") from exc

    effective_analyzer = analyzer or build_image_analyzer()
    return await effective_analyzer.analyze(
        image_bytes=image_bytes,
        mime_type=image_attachment.mime_type,
        file_name=image_attachment.file_name,
        text_hint=event.text,
    )


async def _download_image_file(url: str) -> bytes:
    """Baixa arquivo de imagem para analise com timeout configuravel."""
    try:
        async with httpx.AsyncClient(timeout=settings.image_download_timeout_seconds) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ImageDownloadError(f"Falha ao baixar imagem: status={exc.response.status_code} url={url}") from exc
    except httpx.RequestError as exc:
        raise ImageDownloadError(f"Falha de rede ao baixar imagem: url={url}") from exc

    if not response.content:
        raise ImageDownloadError(f"Arquivo de imagem vazio recebido da URL: {url}")

    return response.content


def _select_image_attachment(attachments: list[NormalizedAttachment]) -> NormalizedAttachment | None:
    for attachment in attachments:
        if attachment.mime_type.lower().startswith("image/"):
            return attachment

    return None
