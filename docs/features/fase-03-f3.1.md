# Fase 3 - Feature 3.1

## O que foi feito

- Implementada estrategia de conexao multi-provider em `db/url.py`.
- Contrato de URLs definido:
  - `DATABASE_URL`: URL principal da aplicacao (runtime async).
  - `DATABASE_URL_MIGRATIONS`: URL sync opcional para Alembic.
- Adicionado fallback automatico para derivar URL sync de migration quando a URL dedicada nao existe.
- Incluida compatibilidade com Supabase e Neon:
  - deteccao de host gerenciado;
  - injecao de `sslmode=require` quando ausente.
- Incluido helper para parametros de engine SQLAlchemy com `pool_pre_ping` e ajuste de `pool_recycle` para provedores gerenciados.

## Ajustes de configuracao

- `app/config.py` agora expoe propriedades:
  - `runtime_database_url`
  - `migrations_database_url`
  - `sqlalchemy_engine_kwargs`
- `.env.example` atualizado com exemplos para Postgres local, Supabase e Neon.

## Testes da feature

- Criado `tests/test_db_url.py` para validar:
  - normalizacao async/sync;
  - prioridade de URL dedicada de migrations;
  - aplicacao de `sslmode=require` em Supabase/Neon;
  - kwargs de engine para ambiente gerenciado.
- `tests/test_config.py` expandido para validar propriedades derivadas de URL.
