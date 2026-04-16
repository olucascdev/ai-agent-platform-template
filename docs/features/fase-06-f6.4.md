# Fase 6 - Feature 6.4

## O que foi feito

- Criado modulo `app/agent/handoff_comments.py` para gerar `comments` estruturados de transferencia humana.
- Definido contrato da feature com `HandoffCommentInput` para consolidar dados de contato, sessao e decisao de conversa.
- Implementada funcao `build_structured_handoff_comment()` com formato deterministico em linhas chave=valor.
- Estrutura de comment inclui campos operacionais para rastreabilidade:
  - intencao e destino (`intent`, `department_key`, `department_id`);
  - contexto do contato (`contact_phone`, `contact_name`, `session_id`);
  - status de qualificacao (`qualification_ready`, `qualification_missing`);
  - resumo da mensagem do cliente (`latest_user_message`) com truncamento seguro.
- Validacao fail-fast adicionada para impedir geracao de comment quando nao existe transferencia ativa.

## Testes da feature

- Criado `tests/test_handoff_comments.py` cobrindo:
  - contrato textual esperado para handoff humano;
  - cenario de lead qualificado com `qualification_missing=none`;
  - erro explicito quando nao ha transferencia ativa.
