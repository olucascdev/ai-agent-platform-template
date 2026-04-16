# Agno Conversational Template

Template base para criar agentes conversacionais por cliente, com webhook FastAPI, memoria persistente e integracoes externas.

## Estado atual

- Runtime simplificado para FastAPI base.
- Endpoint de saude disponivel em `GET /health`.
- Agentes demo do template original removidos do runtime.

## Executando localmente

```sh
cp .env.example .env
docker compose up -d --build
```

API: `http://localhost:8000/docs`

## Testes

```sh
uv run --extra dev pytest
```

## Estrutura util

- `app/`: API principal e modulos de aplicacao.
- `db/`: utilitarios de conexao e acesso a banco.
- `docs/features/`: resumo por feature em PT-BR.
- `docs/phases/`: resumo consolidado por fase em PT-BR.

## Proximas fases

As proximas fases implementam configuracao central, migracoes, lead service, cliente CRM, preprocessor multimodal, agente Agno e webhook completo.
