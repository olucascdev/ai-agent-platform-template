# Fase 5 - Feature 5.4

## O que foi feito

- Criado modulo `app/preprocessing/pdf_processing.py` para processamento de PDF com provider configuravel.
- Definidos contratos e erros da feature:
  - `PdfProcessing`
  - `PdfProcessor` (protocolo)
  - `PdfProcessingError`
  - `PdfAttachmentNotFoundError`
  - `PdfDownloadError`
  - `UnsupportedPdfProcessingProviderError`
- Implementado provider `PyPdfProcessor` com limite de paginas configuravel.
- Implementada factory `build_pdf_processor()` com selecao de provider por configuracao.
- Implementado fluxo `process_pdf_event()` com:
  - selecao do anexo PDF no evento normalizado;
  - download do arquivo via `public_url`;
  - extracao textual usando provider configurado;
  - validacoes fail-fast para anexo ausente/invalido.
- Adicionadas novas configuracoes no `Settings`:
  - `pdf_processing_provider` (default: `pypdf`)
  - `pdf_processing_max_pages` (default: `20`)
  - `pdf_download_timeout_seconds` (default: `20`)
- Atualizado `.env.example` com bloco opcional das variaveis da feature.

## Testes da feature

- Criado `tests/test_pdf_preprocessor.py` cobrindo:
  - fluxo feliz com dependencias injetadas;
  - erro quando nao existe anexo PDF;
  - erro quando anexo PDF nao possui `public_url`;
  - erro de download inesperado convertido para erro de dominio;
  - extracao de texto e limite de paginas no provider pypdf;
  - erro quando nao ha texto extraivel no PDF;
  - selecao de provider padrao e erro para provider nao suportado.
- Expandido `tests/test_config.py` para validar defaults de configuracao de processamento PDF.
