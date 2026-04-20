# Fase 7 - Feature 7.1

## O que foi feito

- Criado endpoint `POST /webhook/whatsapp` em `app/api/webhook.py`.
- Adicionado router dedicado em `app/api/__init__.py` e integrado no `FastAPI` em `app/main.py`.
- Implementado schema validado para webhook em `app/models/webhook.py` com suporte a dois formatos:
  - payload direto no corpo;
  - payload encapsulado em `body`.
- Validacoes de contrato adicionadas no schema:
  - exige `sessionId` ou `session.id`;
  - exige telefone em `contact.phonenumber`, `contact.phone` ou `contact.number`.
- Endpoint retorna `202 Accepted` com resumo canonico do evento aceito (`session_id`, `contact_phone`, `message_id`, `event_id`).
- Integracao com `normalize_incoming_event()` aplicada para consolidar validacao estrutural e normalizacao inicial da entrada.

## Testes da feature

- Criado `tests/test_webhook_whatsapp.py` cobrindo:
  - aceite de payload com wrapper `body`;
  - aceite de payload direto sem wrapper;
  - rejeicao de payload com `body` invalido;
  - rejeicao quando sessao obrigatoria esta ausente;
  - rejeicao quando telefone de contato esta ausente.
