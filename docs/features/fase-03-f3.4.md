# Fase 3 - Feature 3.4

## O que foi feito

- Implementado `LeadService` em `app/core/lead_service.py` com metodos async:
  - `upsert(phone, session_id)`
  - `get_by_phone(phone)`
- Estrategia de `upsert` aplicada conforme contrato:
  1. `INSERT ... ON CONFLICT DO NOTHING`
  2. `UPDATE session_id` quando houver divergencia
  3. `SELECT` final para retornar o registro completo
- Adicionado erro explicito quando o registro nao e encontrado apos o upsert.

## Testes da feature

- Criado `tests/test_lead_service.py` cobrindo:
  - sequencia de statements do upsert;
  - presenca de `ON CONFLICT (phone) DO NOTHING`;
  - consulta por telefone sem commit;
  - erro claro em cenario inesperado sem retorno do lead.
