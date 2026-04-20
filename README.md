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

## Integracao de entrada (oficial)

- Fluxo oficial do template: `CRM/Canal -> POST /webhook/whatsapp -> pipeline interno da API`.
- Nao ha dependencia obrigatoria de n8n no runtime deste projeto.
- Camadas externas de automacao (n8n, iPaaS, etc.) sao opcionais por cliente.

## Provedores de modelo do agente

O agente suporta selecao por ambiente sem alterar codigo:

- `chatgpt` / `openai`
- `openrouter`
- `groq`
- `claude` (Anthropic nativo com `ANTHROPIC_API_KEY` ou via OpenRouter)
- `gemini` (endpoint OpenAI-compatible do Google)

Variaveis opcionais:

- `AGENT_MODEL_PROVIDER`
- `AGENT_MODEL_ID`
- `AGENT_MODEL_API_KEY`
- `AGENT_MODEL_BASE_URL`
- `OPENROUTER_API_KEY`
- `GROQ_API_KEY`
- `ANTHROPIC_API_KEY`

## Estrutura util

- `app/`: API principal e modulos de aplicacao.
- `db/`: utilitarios de conexao e acesso a banco.
- `docs/features/`: resumo por feature em PT-BR.
- `docs/phases/`: resumo consolidado por fase em PT-BR.

## Proximas fases

As proximas fases implementam configuracao central, migracoes, lead service, cliente CRM, preprocessor multimodal, agente Agno e webhook completo.
