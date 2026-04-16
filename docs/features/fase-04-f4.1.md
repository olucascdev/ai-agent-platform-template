# Fase 4 - Feature 4.1

## O que foi feito

- Criado `app/integrations/http_client.py` com `ResilientHttpClient` para chamadas HTTP com timeout e retry.
- Implementadas excecoes dedicadas para erro de rede (`HttpClientRequestError`) e erro de resposta HTTP (`HttpClientResponseError`).
- Definida politica de retry para status transientes (`429`, `500`, `502`, `503`, `504`).
- Adicionado log seguro com redacao de headers sensiveis (`Authorization`, `token`, `x-api-key` e similares).
- Adicionados settings de configuracao HTTP em `app/config.py`:
  - `http_timeout_seconds`
  - `http_max_retries`
  - `http_retry_backoff_seconds`
- Atualizado `.env.example` com os novos parametros opcionais de integracao HTTP.

## Testes da feature

- Criado `tests/test_http_client.py` cobrindo:
  - sucesso sem retry;
  - retry com recuperacao em status retryavel;
  - erro apos esgotar retries em status retryavel;
  - ausencia de retry em status nao retryavel;
  - retry para erro de rede com recuperacao;
  - erro de rede apos esgotar retries;
  - redacao de secrets em logs.
- Expandido `tests/test_config.py` para validar defaults de configuracao HTTP.
