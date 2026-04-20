# Fase 8 - qualidade operacional e seguranca

## Status

- Em andamento.

## Features concluidas

### Feature 8.1 - logs estruturados com correlation id

- Camada de observabilidade adicionada com contexto de `correlation_id` por request.
- Middleware HTTP implementada para propagar `X-Correlation-Id` e gerar id quando ausente.
- Logs estruturados em JSON adicionados para request completion e ciclo do webhook.
- Cobertura automatizada adicionada para campos obrigatorios de log e propagacao de correlation id.

### Feature 8.2 - padrao de erro observavel e auditavel

- Handlers globais de erro adicionados para validacao, HTTP errors, erros de dominio e excecoes inesperadas.
- Envelope de erro padronizado definido com campos auditaveis (`code`, `message`, `error_type`, `correlation_id`, `path`, `method`, `ts`).
- Respostas de erro agora seguem contrato unico em toda API, com `details` controlado por tipo de falha.
- Falha de normalizacao do webhook migrada para erro de dominio auditavel (`webhook.normalization_error`).
- Cobertura automatizada adicionada para contratos de erro 422/404/500 e erro de aplicacao.

## Proximas features da fase

- Feature 8.3 - politica de segredos (sem token hardcoded em codigo/workflow).
- Feature 8.4 - cobertura minima de testes definida.
- Feature 8.5 - validacao de migration no CI.
