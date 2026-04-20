# Fase 7 - Feature 7.3

## O que foi feito

- Implementado servico `WebhookIdempotencyService` em `app/core/webhook_idempotency_service.py` para detectar duplicidade por `event_id`/`message_id`.
- Contrato `IdempotencyDecision` criado para padronizar retorno da validacao (`is_duplicate` + chave utilizada).
- Pipeline de webhook (`app/services/webhook_pipeline.py`) atualizado para checar idempotencia logo apos normalizacao e interromper efeitos colaterais quando evento ja foi processado.
- Resultado do pipeline expandido com metadados de idempotencia (`is_duplicate`, `idempotency_key`).
- Resposta HTTP do endpoint `POST /webhook/whatsapp` agora inclui `is_duplicate` para observabilidade do comportamento idempotente.
- Modelo de banco `ProcessedWebhookEvent` criado em `db/models/webhook_event.py`.
- Migration `migrations/versions/20260420_0002_create_processed_webhook_events_table.py` adicionada com:
  - tabela `processed_webhook_events`;
  - unique indexes para `event_id` e `message_id`;
  - check constraint exigindo ao menos um identificador.

## Testes da feature

- Criado `tests/test_webhook_idempotency_service.py` cobrindo:
  - evento inedito com insert bem-sucedido;
  - evento duplicado por conflito;
  - skip de idempotencia quando identificadores nao existem.
- Criado `tests/test_webhook_event_model.py` com contrato estrutural do modelo de idempotencia.
- `tests/test_webhook_pipeline_service.py` expandido com cenario de short-circuit para evento duplicado.
- `tests/test_webhook_whatsapp.py` expandido para validar retorno `is_duplicate=true` quando pipeline marca duplicidade.
- `tests/test_migration_contract.py` atualizado para validar presenca da migration da fase 7.3.
