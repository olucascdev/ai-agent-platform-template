# Fase 9 - Feature 9.1

## O que foi feito

- Criado workflow base n8n em `n8n/workflows/whatsapp-template-base.json`.
- Workflow preparado para uso plugavel com:
  - URL de API por env var (`API_PLATFORM_BASE_URL`);
  - timeout por env var (`API_PLATFORM_TIMEOUT_MS`);
  - autenticacao por credencial n8n (`HTTP Header Auth`) sem token hardcoded.
- Fluxo base implementado:
  - `Webhook` (entrada);
  - `HTTP Request` para `POST /webhook/whatsapp`;
  - `Respond to Webhook` com retorno `202`.
- Adicionado guia operacional em `n8n/README.md` e exemplo de env em `n8n/.env.example`.

## Testes da feature

- Criado `tests/test_n8n_template_base.py` cobrindo:
  - estrutura importavel minima do workflow;
  - uso de env vars para URL/timeout;
  - binding de credencial n8n no node HTTP;
  - ausencia de token hardcoded no JSON do workflow.
