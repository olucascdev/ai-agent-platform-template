# Fase 2 - Feature 2.1

## O que foi feito

- Criado `app/config.py` com `pydantic-settings` como fonte unica de configuracao.
- Centralizadas variaveis obrigatorias de ambiente do template:
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY`
  - `DATABASE_URL`
  - `CRM_BASE_URL`
  - `CRM_TOKEN`
  - `WHATSAPP_SENDER_URL`
  - `WHATSAPP_TOKEN`
  - `AGENT_NAME`
  - `AGENT_SESSION_PREFIX`
  - `MESSAGE_DELAY_SECONDS` (padrao `3`)
- Implementado carregamento fail-fast via `settings = get_settings()` para falhar ja na inicializacao.
- `app/main.py` atualizado para consumir configuracao central e validar carga de settings no bootstrap.

## Testes da feature

- Criado `tests/test_config.py` para validar:
  - aplicacao do valor padrao de `message_delay_seconds`;
  - falha de validacao quando variavel obrigatoria esta ausente.
- Criado `tests/conftest.py` para padronizar variaveis obrigatorias no ambiente de testes.
