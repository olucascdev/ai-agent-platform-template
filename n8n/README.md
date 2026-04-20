# n8n Base Template (F09.1)

This folder contains the base n8n workflow template for inbound WhatsApp events.

## Files

- `workflows/whatsapp-template-base.json`: importable workflow for `POST /webhook/whatsapp`.
- `.env.example`: suggested environment variables used by workflow expressions.

## Required n8n setup

1. Create an `HTTP Header Auth` credential in n8n.
2. Name it `AI Platform Header Auth` (or rebind the node after import).
3. Configure header name/value expected by your API gateway (for example `Authorization: Bearer <token>`).

## Required env vars

- `API_PLATFORM_BASE_URL`
- `API_PLATFORM_TIMEOUT_MS` (optional, defaults to `20000` in expressions)

## Import notes

- Import `workflows/whatsapp-template-base.json` in a clean n8n instance.
- Review Webhook path and credential binding before activation.
