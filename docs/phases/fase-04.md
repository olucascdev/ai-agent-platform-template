# Fase 4 - integracoes externas HTTP

## Status

- Em andamento.

## Features concluidas

### Feature 4.1 - cliente HTTP resiliente

- `ResilientHttpClient` implementado com timeout, retry e backoff exponencial.
- Excecoes de rede e resposta HTTP padronizadas para consumo pelos adapters de CRM/Sender.
- Logs de retry com redacao de headers sensiveis para evitar vazamento de segredo.
- Configuracao de runtime adicionada via settings:
  - `HTTP_TIMEOUT_SECONDS`
  - `HTTP_MAX_RETRIES`
  - `HTTP_RETRY_BACKOFF_SECONDS`
- Cobertura automatizada adicionada para contrato de resiliencia HTTP.

## Proximas features da fase

- Feature 4.2 - adapter de CRM configuravel por cliente.
- Feature 4.3 - adapter de sender WhatsApp configuravel por cliente.
- Feature 4.4 - consolidacao de politica de erro/retry por tipo de integracao.
- Feature 4.5 - fechamento de contratos HTTP e testes de integracao simulada.
