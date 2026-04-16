# Fase 5 - Feature 5.1

## O que foi feito

- Criado modulo `app/preprocessing/event_normalizer.py` para normalizar payload bruto em evento canonico interno.
- Definidos contratos tipados:
  - `NormalizedIncomingEvent`
  - `NormalizedAttachment`
  - `EventNormalizationError`
- Implementada funcao `normalize_incoming_event(payload)` com suporte aos formatos de entrada mais comuns do webhook.
- Regras de normalizacao adicionadas:
  - unwrap automatico de payload em `body` quando presente;
  - extracao padrao de `session_id`, `contact_phone`, `text`, metadados e anexos;
  - deduplicacao de anexos entre `lastMessagesAggregated.files` e `lastMessage.file`;
  - classificacao de `input_type` em `text`, `audio`, `image`, `pdf` ou `other`.
- Validacoes fail-fast adicionadas para campos obrigatorios (`session_id` e `contact_phone`).

## Testes da feature

- Criado `tests/test_event_normalizer.py` cobrindo:
  - normalizacao de evento de texto;
  - classificacao de audio/imagem/pdf;
  - fallback de anexo vindo de `lastMessage.file`;
  - deduplicacao de anexo duplicado;
  - erros explicitos para ausencia de `session_id` e `contact_phone`.
