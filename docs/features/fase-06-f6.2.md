# Fase 6 - Feature 6.2

## O que foi feito

- Criado modulo `app/agent/session.py` com helper `build_single_client_session_id()`.
- Implementada composicao de sessao no formato `AGENT_SESSION_PREFIX:telefone_normalizado`.
- Normalizacao de telefone aplicada para manter apenas digitos e evitar variacao de formato na mesma conversa.
- Validacoes fail-fast adicionadas para:
  - `contact_phone` vazio ou sem digitos;
  - `session_prefix` vazio.
- `AgentFactory` atualizado em `app/agent/factory.py` com `build_for_phone()` para criar agente ja com sessao single-client derivada do telefone.
- Export do helper de sessao adicionado em `app/agent/__init__.py`.

## Testes da feature

- Criado `tests/test_agent_session.py` cobrindo:
  - formato de sessao com prefixo explicito;
  - fallback de prefixo via `AGENT_SESSION_PREFIX`;
  - erros para telefone invalido e prefixo em branco.
- Expandido `tests/test_agent_factory.py` com cenario de `build_for_phone()` para validar derivacao de `session_id` e propagacao de `user_id`.
