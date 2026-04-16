# Fase 5 - Feature 5.3

## O que foi feito

- Criado modulo `app/preprocessing/image_analysis.py` para analise de imagem com provider configuravel.
- Definidos contratos e erros da feature:
  - `ImageAnalysis`
  - `ImageAnalyzer` (protocolo)
  - `ImageAnalysisError`
  - `ImageAttachmentNotFoundError`
  - `ImageDownloadError`
  - `UnsupportedImageAnalysisProviderError`
- Implementado provider `GoogleImageAnalyzer` com:
  - suporte a model configuravel;
  - prompt base configuravel;
  - enriquecimento de prompt com contexto textual do evento (`text_hint`).
- Implementada factory `build_image_analyzer()` com selecao de provider por configuracao.
- Implementado fluxo `analyze_image_event()` com:
  - selecao do anexo de imagem no evento normalizado;
  - download da imagem por `public_url`;
  - execucao da analise no provider selecionado;
  - validacoes fail-fast para anexo ausente/invalido.
- Adicionadas novas configuracoes no `Settings`:
  - `image_analysis_provider` (default: `google`)
  - `image_analysis_model` (default: `models/gemini-2.0-flash-lite`)
  - `image_analysis_prompt` (default textual)
  - `image_download_timeout_seconds` (default: `20`)
- Atualizado `.env.example` com bloco opcional das variaveis da feature.

## Testes da feature

- Criado `tests/test_image_preprocessor.py` cobrindo:
  - fluxo feliz com dependencias injetadas;
  - erro quando nao existe anexo de imagem;
  - erro quando anexo de imagem nao possui `public_url`;
  - erro de download inesperado convertido para erro de dominio;
  - contrato de chamada do provider Google sem dependencia externa;
  - fallback de extracao de texto por `candidates`;
  - erro quando provider retorna analise vazia;
  - selecao de provider padrao e erro para provider nao suportado.
- Expandido `tests/test_config.py` para validar defaults de configuracao de analise de imagem.
