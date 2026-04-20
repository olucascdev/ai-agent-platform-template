# Fase 8 - Feature 8.5

## O que foi feito

- Workflow de CI atualizado em `.github/workflows/validate.yml` para validar migrations contra banco real no pipeline:
  - provisionamento de service PostgreSQL dedicado no job `validate`;
  - variaveis `DATABASE_URL` e `DATABASE_URL_MIGRATIONS` apontando para o banco de CI.
- Etapa de validacao de migration adicionada ao CI com execucao completa de ciclo:
  - `alembic upgrade head`;
  - `alembic downgrade base`;
  - `alembic upgrade head` novamente para garantir reversibilidade e reaplicacao.
- Gate de migration agora roda antes de mypy/pytest, evitando merge com cadeia de migration quebrada.

## Testes da feature

- Criado `tests/test_validate_workflow_migrations.py` cobrindo:
  - presenca do service Postgres no workflow de validacao;
  - presenca da etapa CI que executa upgrade/downgrade/upgrade de migrations.
