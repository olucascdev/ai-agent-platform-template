"""Testes da feature 5.3 de analise de imagem configuravel."""

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.config import settings
from app.preprocessing import (
    GoogleImageAnalyzer,
    ImageAnalysis,
    ImageAnalysisError,
    ImageAttachmentNotFoundError,
    ImageDownloadError,
    UnsupportedImageAnalysisProviderError,
    analyze_image_event,
    build_image_analyzer,
)
from app.preprocessing.event_normalizer import NormalizedAttachment, NormalizedIncomingEvent


def _build_event(*, attachments: list[NormalizedAttachment], text: str | None = None) -> NormalizedIncomingEvent:
    return NormalizedIncomingEvent(
        session_id="sessao-1",
        contact_phone="+5531999999999",
        input_type="image",
        text=text,
        attachments=attachments,
        message_id="msg-1",
        message_created_at="2026-04-16T12:00:00Z",
        message_type_raw="IMAGE",
        contact_name="Joel",
        channel_platform="WhatsApp",
    )


@dataclass
class _FakeAnalyzer:
    captured_image_bytes: bytes | None = None
    captured_mime_type: str | None = None
    captured_file_name: str | None = None
    captured_text_hint: str | None = None

    async def analyze(
        self,
        *,
        image_bytes: bytes,
        mime_type: str,
        file_name: str | None,
        text_hint: str | None,
    ) -> ImageAnalysis:
        self.captured_image_bytes = image_bytes
        self.captured_mime_type = mime_type
        self.captured_file_name = file_name
        self.captured_text_hint = text_hint
        return ImageAnalysis(text="texto da imagem", provider="fake", model="fake-1")


@pytest.mark.asyncio
async def test_analyze_image_event_happy_path_with_injected_dependencies() -> None:
    """Analisa imagem com downloader/provider injetados no fluxo principal."""
    event = _build_event(
        text="envio de comprovante",
        attachments=[
            NormalizedAttachment(
                mime_type="image/png",
                public_url="https://cdn.exemplo.com/imagem.png",
                file_name="imagem.png",
                file_id="img-1",
            )
        ],
    )

    fake_analyzer = _FakeAnalyzer()

    async def fake_downloader(url: str) -> bytes:
        assert url == "https://cdn.exemplo.com/imagem.png"
        return b"image-bytes"

    result = await analyze_image_event(event, analyzer=fake_analyzer, downloader=fake_downloader)

    assert result.text == "texto da imagem"
    assert fake_analyzer.captured_image_bytes == b"image-bytes"
    assert fake_analyzer.captured_mime_type == "image/png"
    assert fake_analyzer.captured_file_name == "imagem.png"
    assert fake_analyzer.captured_text_hint == "envio de comprovante"


@pytest.mark.asyncio
async def test_analyze_image_event_raises_when_no_image_attachment_exists() -> None:
    """Falha quando evento nao possui anexo de imagem."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="audio/ogg",
                public_url="https://cdn.exemplo.com/audio.ogg",
                file_name="audio.ogg",
                file_id="a-1",
            )
        ]
    )

    async def fake_downloader(_url: str) -> bytes:
        return b"x"

    with pytest.raises(ImageAttachmentNotFoundError) as exc_info:
        await analyze_image_event(event, analyzer=_FakeAnalyzer(), downloader=fake_downloader)

    assert "nao contem anexo de imagem" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_analyze_image_event_raises_when_image_has_no_public_url() -> None:
    """Falha quando anexo de imagem existe mas sem URL de download."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="image/jpeg",
                public_url=None,
                file_name="imagem.jpg",
                file_id="img-2",
            )
        ]
    )

    async def fake_downloader(_url: str) -> bytes:
        return b"x"

    with pytest.raises(ImageAttachmentNotFoundError) as exc_info:
        await analyze_image_event(event, analyzer=_FakeAnalyzer(), downloader=fake_downloader)

    assert "public_url" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyze_image_event_wraps_unexpected_download_failure() -> None:
    """Converte erro inesperado no downloader para erro de dominio da feature."""
    event = _build_event(
        attachments=[
            NormalizedAttachment(
                mime_type="image/png",
                public_url="https://cdn.exemplo.com/imagem.png",
                file_name="imagem.png",
                file_id="img-3",
            )
        ]
    )

    async def broken_downloader(_url: str) -> bytes:
        raise RuntimeError("falha inesperada")

    with pytest.raises(ImageDownloadError) as exc_info:
        await analyze_image_event(event, analyzer=_FakeAnalyzer(), downloader=broken_downloader)

    assert "falha inesperada" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_google_image_analyzer_sends_expected_payload_to_model() -> None:
    """Valida contrato de chamada do provider Google sem API externa."""

    class _FakeModel:
        def __init__(self) -> None:
            self.last_payload: list[object] = []

        def generate_content(self, payload: list[object]) -> object:
            self.last_payload = payload
            return SimpleNamespace(text="  texto analisado  ")

    fake_model = _FakeModel()
    analyzer = GoogleImageAnalyzer(
        model="models/gemini-2.0-flash-lite",
        prompt="Extraia o texto da imagem.",
        api_key="fake-key",
        model_client=fake_model,
    )

    result = await analyzer.analyze(
        image_bytes=b"img-bytes",
        mime_type="image/png",
        file_name="imagem.png",
        text_hint="comprovante em anexo",
    )

    assert result.text == "texto analisado"
    assert result.provider == "google"
    assert result.model == "models/gemini-2.0-flash-lite"
    assert isinstance(fake_model.last_payload[0], str)
    assert "Contexto adicional" in fake_model.last_payload[0]
    payload_entry = fake_model.last_payload[1]
    assert isinstance(payload_entry, dict)
    inline_data_obj = payload_entry.get("inline_data")
    assert isinstance(inline_data_obj, dict)
    inline_data = inline_data_obj
    assert inline_data["mime_type"] == "image/png"
    assert inline_data["data"] == b"img-bytes"


@pytest.mark.asyncio
async def test_google_image_analyzer_extracts_text_from_candidates_fallback() -> None:
    """Usa fallback em candidates quando resposta nao possui atributo `text`."""

    class _FakeModel:
        def generate_content(self, _payload: list[object]) -> object:
            return SimpleNamespace(
                text=None,
                candidates=[
                    SimpleNamespace(
                        content=SimpleNamespace(
                            parts=[SimpleNamespace(text="Parte 1"), SimpleNamespace(text="Parte 2")]
                        )
                    )
                ],
            )

    analyzer = GoogleImageAnalyzer(
        model="models/gemini-2.0-flash-lite",
        prompt="Extraia texto",
        api_key="fake-key",
        model_client=_FakeModel(),
    )

    result = await analyzer.analyze(
        image_bytes=b"img-bytes",
        mime_type="image/jpeg",
        file_name="imagem.jpg",
        text_hint=None,
    )

    assert result.text == "Parte 1\nParte 2"


@pytest.mark.asyncio
async def test_google_image_analyzer_raises_when_response_has_no_text() -> None:
    """Falha quando provider retorna resposta sem texto util."""

    class _FakeModel:
        def generate_content(self, _payload: list[object]) -> object:
            return SimpleNamespace(text="   ", candidates=[])

    analyzer = GoogleImageAnalyzer(
        model="models/gemini-2.0-flash-lite",
        prompt="Extraia texto",
        api_key="fake-key",
        model_client=_FakeModel(),
    )

    with pytest.raises(ImageAnalysisError) as exc_info:
        await analyzer.analyze(
            image_bytes=b"img-bytes",
            mime_type="image/jpeg",
            file_name="imagem.jpg",
            text_hint=None,
        )

    assert "analise vazia" in str(exc_info.value).lower()


def test_build_image_analyzer_uses_google_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Monta provider Google quando configuracao padrao esta ativa."""
    monkeypatch.setattr(settings, "image_analysis_provider", "google")
    monkeypatch.setattr(settings, "image_analysis_model", "models/gemini-2.0-flash-lite")
    monkeypatch.setattr(settings, "image_analysis_prompt", "Extraia texto")

    analyzer = build_image_analyzer(model_client=SimpleNamespace(generate_content=lambda _payload: None))

    assert isinstance(analyzer, GoogleImageAnalyzer)


def test_build_image_analyzer_raises_for_unsupported_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Falha explicitamente para provider de imagem nao suportado."""
    monkeypatch.setattr(settings, "image_analysis_provider", "desconhecido")

    with pytest.raises(UnsupportedImageAnalysisProviderError) as exc_info:
        build_image_analyzer(model_client=SimpleNamespace(generate_content=lambda _payload: None))

    assert "nao suportado" in str(exc_info.value).lower()
