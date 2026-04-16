# Fase 3 - Feature 3.2

## O que foi feito

- Criada base declarativa do SQLAlchemy em `db/base.py`.
- Implementado modelo `Lead` em `db/models/lead.py` com contrato da fase:
  - `id`
  - `phone` (unico)
  - `session_id`
  - `crm_contact_id`
  - `created_at`
  - `updated_at`
- Implementada camada de sessao async em `db/session.py`:
  - `async_engine`
  - `AsyncSessionLocal`
  - `get_async_session()`
- Atualizado `db/__init__.py` para exportar utilitarios novos e manter import tardio para evitar ciclo.

## Testes da feature

- Criado `tests/test_lead_model.py` para validar estrutura e constraint de unicidade.
- Criado `tests/test_db_session.py` para validar engine async e provider de sessao.
