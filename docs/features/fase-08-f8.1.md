# Fase 8 - Feature 8.1

## O que foi feito

- Criada camada de observabilidade em `app/observability/` com:
  - contexto de `correlation_id` por request (`contextvars`);
  - helper de log estruturado em JSON (`log_structured`).
- Middleware HTTP adicionada em `app/main.py` para:
  - aceitar `X-Correlation-Id` de entrada (ou gerar automaticamente);
  - propagar `X-Correlation-Id` no response;
  - registrar evento estruturado `http_request_completed` com campos operacionais (`method`, `path`, `status_code`, `duration_ms`, `error_type`).
- Endpoint `POST /webhook/whatsapp` atualizado para logs estruturados de ciclo de vida:
  - `webhook_whatsapp_received`;
  - `webhook_whatsapp_accepted`;
  - `webhook_whatsapp_rejected` (warn em erro de validacao).

## Testes da feature

- Criado `tests/test_observability_logging.py` cobrindo:
  - presenca de campos obrigatorios de log estruturado com `correlation_id` fixo;
  - propagacao de correlation id no header de resposta;
  - geracao automatica de correlation id quando header nao e enviado.
