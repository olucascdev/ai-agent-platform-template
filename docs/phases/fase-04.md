# Fase 4 - integracoes externas HTTP

## Status

- Concluida.

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

### Feature 4.2 - cliente CRM configuravel

- `CRMClient` implementado com operacoes de lookup por telefone e transferencia por departamento.
- Factory `build_crm_client()` adicionada para inicializar integracao com settings centralizados.
- Contratos de autenticacao, paths e query params do CRM tornados configuraveis por ambiente.
- Compatibilidade adicionada para formatos de resposta comuns (`data[]` e objeto unico com `id`).
- Cobertura automatizada adicionada para contrato do cliente CRM.

### Feature 4.3 - cliente sender WhatsApp configuravel

- `WhatsAppSenderClient` implementado para envio de texto com contrato HTTP configuravel.
- Factory `build_whatsapp_sender_client()` adicionada para inicializar o sender com settings centralizados.
- URL completa do sender agora suportada com parse de base + path + query.
- Contratos de autenticacao e payload do sender tornados configuraveis por ambiente.
- Cobertura automatizada adicionada para contrato do sender e cenarios de configuracao.

### Feature 4.4 - politica de erro/retry por integracao

- Politicas de retry consolidadas em modulo dedicado (`retry_policy.py`).
- Contratos de status retryavel separados por tipo de integracao (CRM e sender WhatsApp).
- Builders de CRM e sender passaram a usar politicas padronizadas, mantendo configuracao global de retries/backoff.
- Cobertura automatizada adicionada para contrato das politicas e cenarios de retry especificos por integracao.

### Feature 4.5 - fechamento de contratos HTTP e testes de integracao simulada

- Contratos HTTP de CRM e sender consolidados em documentacao tecnica da fase.
- Testes de integracao simulada adicionados para fluxo ponta a ponta (lookup, transferencia e envio).
- Validacao automatizada adicionada para diferenca de politica de retry entre CRM e sender.

### Feature 4.6 - validacao de contrato por adapter em runtime

- Camada dedicada de validacao de payload HTTP implementada para CRM e sender.
- Erros de contrato agora sao explicitados por `IntegrationContractError` para facilitar diagnostico.
- Validacoes de entrada obrigatoria adicionadas nos clients para evitar requests invalidos.
- Cobertura automatizada adicionada para cenarios de payload invalido e campos obrigatorios ausentes.

## Proximas features da fase

- Nenhuma. Fase 4 finalizada.
