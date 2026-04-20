# Fase 8 - qualidade operacional e seguranca

## Status

- Concluida.

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

### Feature 8.3 - politica de segredos (sem token hardcoded em codigo/workflow)

- Politica de segredos implementada com varredura de codigo, workflows e scripts.
- Regras adicionadas para bloquear valores literais em variaveis sensiveis e padroes de tokens reais.
- Script de enforcement criado para uso local/CI (`scripts/check_secrets_policy.py`).
- Workflow de validacao e script local de validacao atualizados para executar a politica automaticamente.
- Cobertura automatizada adicionada para cenarios de deteccao e garantia de repositorio limpo.

### Feature 8.4 - cobertura minima de testes definida

- Politica minima de cobertura definida com `pytest-cov` e threshold obrigatorio.
- Testes passaram a executar cobertura por padrao com escopo em `app` e `db`.
- Gate de qualidade configurado com `--cov-fail-under=85`.
- Configuracao declarativa de cobertura adicionada para branch coverage e relatorio padrao.
- Cobertura automatizada adicionada para validar contrato de politica no `pyproject.toml`.

### Feature 8.5 - validacao de migration no CI

- Workflow `validate` atualizado para provisionar Postgres dedicado no job de CI.
- Validacao de migrations adicionada com ciclo `upgrade -> downgrade -> upgrade` no pipeline.
- Ambiente CI agora exporta `DATABASE_URL`/`DATABASE_URL_MIGRATIONS` para execucao real do Alembic.
- Gate de migration executa antes de type-check e testes, bloqueando merges com cadeia de migration quebrada.
- Cobertura automatizada adicionada para contratos do workflow de migration no CI.

## Proximas features da fase

- Nenhuma. Fase 8 finalizada.
