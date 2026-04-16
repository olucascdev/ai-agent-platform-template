# Fase 3 - banco e lead service

## Status

- Em andamento.

## Features concluidas

### Feature 3.1 - estrategia de conexao multi-provider

- Contrato de URLs separado para runtime e migrations.
- Compatibilidade com Supabase, Neon e Postgres local.
- Fallback de URL sync implementado para Alembic.
- Testes cobrindo normalizacao, SSL e configuracao de engine.

## Proximas features da fase

- Feature 3.2: base async SQLAlchemy e modelo `leads`.
- Feature 3.3: setup Alembic e migration inicial.
- Feature 3.4: implementacao do `lead_service`.
