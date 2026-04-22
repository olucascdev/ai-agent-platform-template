# Contratos HTTP da fase 4

## Objetivo

Consolidar os contratos de request/response das integracoes HTTP do template para reduzir risco de quebra ao trocar CRM ou sender por cliente.

## CRM - busca de contato

- Metodo: `GET`
- Path: configuravel via `CRM_CONTACTS_LOOKUP_PATH` (default: `/contacts`)
- Query params:
  - telefone: `CRM_LOOKUP_PHONE_PARAM` + `CRM_LOOKUP_PHONE_VALUE_TEMPLATE`
  - service id opcional: `CRM_LOOKUP_SERVICE_ID_PARAM` com `CRM_SERVICE_ID`
- Header de autenticacao:
  - nome: `CRM_AUTH_HEADER_NAME` (default: `Authorization`)
  - prefixo: `CRM_AUTH_HEADER_PREFIX` (default: `Bearer`)
  - valor base: `CRM_TOKEN`

### Formatos de resposta aceitos

1. Objeto unico:

```json
{
  "id": "contact-123",
  "name": "Maria"
}
```

2. Lista em `data`:

```json
{
  "data": [
    {
      "id": "contact-123"
    }
  ]
}
```

## CRM - transferencia de atendimento

- Metodo: `POST`
- Path: `CRM_TRANSFER_PATH_TEMPLATE` com `{contact_id}`
- Body JSON padrao:

```json
{
  "departmentId": "dep-1",
  "comments": "Lead qualificado e pronto para comercial."
}
```

## Sender WhatsApp - envio de texto

- Metodo: configuravel via `WHATSAPP_SENDER_METHOD` (default: `POST`)
- URL: `WHATSAPP_SENDER_URL` (URL completa)
  - Pode conter placeholders: `{session_id}`, `{sessionId}`, `{phone}`, `{number}`
- Header de autenticacao:
  - nome: `WHATSAPP_SENDER_AUTH_HEADER_NAME` (default: `Authorization`)
  - prefixo: `WHATSAPP_SENDER_AUTH_HEADER_PREFIX` (default: `Bearer`)
  - valor base: `WHATSAPP_TOKEN`
- Body JSON configuravel:
  - incluir telefone no body: `WHATSAPP_SENDER_INCLUDE_NUMBER` (default: `true`)
  - campo telefone: `WHATSAPP_SENDER_NUMBER_FIELD` (default: `number`)
  - campo texto: `WHATSAPP_SENDER_TEXT_FIELD` (default: `text`)

### Exemplo padrao de payload

```json
{
  "number": "+5531999999999",
  "text": "Ola! Recebemos sua solicitacao."
}
```

### Exemplo WTS/Helena por session

```env
WHATSAPP_SENDER_URL=https://api.wts.chat/chat/v1/session/{session_id}/message
WHATSAPP_SENDER_INCLUDE_NUMBER=false
WHATSAPP_SENDER_TEXT_FIELD=text
```

## Politica de retry por integracao

### CRM

- Status retryavel: `408`, `429`, `500`, `502`, `503`, `504`

### Sender WhatsApp

- Status retryavel: `408`, `409`, `425`, `429`, `500`, `502`, `503`, `504`

## Seguranca

- Headers sensiveis sao redigidos (`<redacted>`) nos logs do cliente HTTP.
- Tokens nao devem ser hardcoded no codigo; sempre via variaveis de ambiente.

## Validacao de contrato em runtime

- A aplicacao valida payloads HTTP com utilitarios centralizados em `app/integrations/contracts.py`.
- Quando o provider retorna payload fora do contrato esperado, e levantado `IntegrationContractError`.
- O objetivo e falhar de forma explicita e rastreavel, evitando seguir o fluxo com dados inconsistentes.
