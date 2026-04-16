# Fase 3 - Feature 3.3

## O que foi feito

- Configurado Alembic no projeto com:
  - `alembic.ini`
  - `migrations/env.py`
  - `migrations/script.py.mako`
  - `migrations/versions/`
- Criado `db/alembic_config.py` para resolver URL de migration sem depender dos settings completos da API.
- Implementada migration inicial `20260416_0001_create_leads_table.py` com criacao da tabela `leads`.
- Estrategia de migration padronizada para driver asyncpg (compativel com stack atual e sem dependencia sync extra).

## Estrutura de migration inicial

- Tabela `leads` com colunas:
  - `id`
  - `phone` (unico)
  - `session_id`
  - `crm_contact_id`
  - `created_at`
  - `updated_at`
- Indice `ix_leads_session_id` para consultas por sessao.

## Testes da feature

- `tests/test_alembic_config.py`:
  - prioridade de `DATABASE_URL_MIGRATIONS`;
  - metadata incluindo tabela `leads`.
- `tests/test_migration_contract.py`:
  - contrato da migration inicial;
  - configuracao do `alembic.ini`.
