# Fase 4 - Feature 4.4

## O que foi feito

- Criado `app/integrations/retry_policy.py` para consolidar politica de retry por tipo de integracao.
- Definidos contratos de status retryavel:
  - CRM: `408`, `429`, `500`, `502`, `503`, `504`.
  - Sender WhatsApp: `408`, `409`, `425`, `429`, `500`, `502`, `503`, `504`.
- Implementada dataclass `RetryPolicy` para padronizar `max_retries`, `retry_backoff_seconds` e `retry_status_codes`.
- Adicionados builders de politica:
  - `build_crm_retry_policy()`
  - `build_whatsapp_sender_retry_policy()`
- Integrado o uso de politica no `build_crm_client()` e no `build_whatsapp_sender_client()`.
- `build_crm_client()` atualizado para aceitar `transport` opcional, alinhando com o sender e facilitando testes de contrato.

## Testes da feature

- Criado `tests/test_retry_policy.py` para validar contratos oficiais de retry por integracao.
- Expandido `tests/test_crm_client.py` com cenario de retry em `408` no builder de CRM.
- Expandido `tests/test_whatsapp_sender_client.py` com cenario de retry em `425` no builder de sender.
