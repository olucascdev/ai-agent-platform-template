# Fase 1 - Feature 1.2

## O que foi feito

- Criado `.env.example` como fonte oficial de configuracao por cliente.
- Documentadas em PT-BR todas as variaveis obrigatorias com explicacao de uso.
- Definido valor padrao de `MESSAGE_DELAY_SECONDS=3` no template.
- Atualizado `README.md` para usar `cp .env.example .env`.
- Removido `example.env` antigo para evitar duplicidade e confusao no onboarding.

## Variaveis obrigatorias documentadas

- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `DATABASE_URL`
- `CRM_BASE_URL`
- `CRM_TOKEN`
- `WHATSAPP_SENDER_URL`
- `WHATSAPP_TOKEN`
- `AGENT_NAME`
- `AGENT_SESSION_PREFIX`
- `MESSAGE_DELAY_SECONDS`

## Testes da feature

- Criado `tests/test_env_example.py` para validar:
  - presenca de todas as chaves obrigatorias;
  - valor padrao do delay de envio.
