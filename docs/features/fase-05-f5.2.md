# Fase 5 - Feature 5.2

## O que foi feito

- Criado modulo `app/preprocessing/audio_transcription.py` para transcricao de audio com provider configuravel.
- Definidos contratos e erros da feature:
  - `AudioTranscription`
  - `AudioTranscriber` (protocolo)
  - `AudioTranscriptionError`
  - `AudioAttachmentNotFoundError`
  - `AudioDownloadError`
  - `UnsupportedAudioTranscriptionProviderError`
- Implementado provider `OpenAIAudioTranscriber` com suporte a model e language configuraveis.
- Implementada factory `build_audio_transcriber()` com selecao por `audio_transcription_provider`.
- Implementado fluxo `transcribe_audio_event()` com:
  - selecao do anexo de audio;
  - download de arquivo via `public_url`;
  - execucao de transcricao no provider selecionado;
  - validacoes fail-fast para anexo ausente/invalido.
- Adicionadas novas configuracoes no `Settings`:
  - `audio_transcription_provider` (default: `openai`)
  - `audio_transcription_model` (default: `whisper-1`)
  - `audio_transcription_language` (opcional)
  - `audio_download_timeout_seconds` (default: `20`)
- Atualizado `.env.example` com bloco opcional das variaveis da feature.

## Testes da feature

- Criado `tests/test_audio_preprocessor.py` cobrindo:
  - fluxo feliz com dependencias injetadas;
  - erro quando nao existe anexo de audio;
  - erro quando anexo de audio nao possui `public_url`;
  - erro de download inesperado convertido para erro de dominio;
  - contrato de chamada do provider OpenAI sem dependencia externa;
  - erro quando provider retorna transcricao vazia;
  - selecao de provider padrao e erro para provider nao suportado.
- Expandido `tests/test_config.py` para validar defaults da configuracao de transcricao.
