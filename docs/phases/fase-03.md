# Fase 3 - banco e lead service

## Status

- Concluida.

## Consolidado da fase

- Estrategia de conexao multi-provider implementada para Postgres local, Supabase e NeonDB.
- Camada async SQLAlchemy concluida com modelo `Lead` e sessao padrao (`async_engine`, `AsyncSessionLocal`, `get_async_session`).
- Alembic configurado com migration inicial da tabela `leads`.
- `LeadService` implementado com `upsert` idempotente e `get_by_phone`.

## Matriz de suporte (DSN)

### Postgres local

```env
DATABASE_URL=postgresql+asyncpg://ai:ai@localhost:5432/ai
# Opcional: URL dedicada para migrations
DATABASE_URL_MIGRATIONS=postgresql+asyncpg://ai:ai@localhost:5432/ai
```

### Supabase

```env
DATABASE_URL=postgresql+asyncpg://postgres:[SENHA]@db.[PROJECT-REF].supabase.co:5432/postgres
# Opcional: usar conexao dedicada para migrations
DATABASE_URL_MIGRATIONS=postgresql+asyncpg://postgres:[SENHA]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### NeonDB

```env
DATABASE_URL=postgresql+asyncpg://[USER]:[SENHA]@[ENDPOINT].neon.tech:5432/[DATABASE]
# Opcional: usar conexao dedicada para migrations
DATABASE_URL_MIGRATIONS=postgresql+asyncpg://[USER]:[SENHA]@[ENDPOINT].neon.tech:5432/[DATABASE]
```

## Guia rapido: app URL vs migrations URL

- `DATABASE_URL`: URL principal usada pela aplicacao em runtime (FastAPI + services async).
- `DATABASE_URL_MIGRATIONS`: URL opcional usada pelo Alembic.
- Se `DATABASE_URL_MIGRATIONS` nao for definida, o projeto deriva automaticamente a partir de `DATABASE_URL`.
- Para Supabase/Neon, `sslmode=require` e aplicado automaticamente quando ausente.
- Regra pratica:
  - `DATABASE_URL` sempre obrigatoria.
  - `DATABASE_URL_MIGRATIONS` recomendada quando quiser separar credencial/rota de migration da aplicacao.

## Validacao da fase

- Suite de testes completa da fase executada com sucesso.
- Comandos de validacao:
  - `uv run python -m pytest`
  - `uv run ruff check .`
  - `uv run --with mypy python -m mypy .`

## Historico de features

- Feature 3.1: estrategia de conexao multi-provider.
- Feature 3.2: base async e modelo `leads`.
- Feature 3.3: setup Alembic e migration inicial.
- Feature 3.4: implementacao do `LeadService`.
- Feature 3.5: fechamento da fase com matriz de suporte e guia operacional.
