# Fase 7 - Feature 7.5

## O que foi feito

- Persistencia de metadados de pipeline implementada no `LeadService` com metodo `update_metadata_by_phone(...)`.
- Pipeline de webhook (`app/services/webhook_pipeline.py`) atualizado para gravar metadados operacionais por telefone:
  - `crm_contact_id` quando lookup CRM retorna contato;
  - `status` do fluxo (`message_sent`, `session_reset`, `duplicate_ignored`).
- Modelo `Lead` expandido com coluna `status` em `db/models/lead.py`.
- Migration `migrations/versions/20260420_0003_add_status_to_leads.py` adicionada para persistir coluna `status` + indice `ix_leads_status`.
- Resultado interno do pipeline ampliado com `lead_status` para facilitar auditoria e debug das execucoes.

## Testes da feature

- `tests/test_lead_service.py` expandido com cenarios de update de metadados e skip seguro sem valores validos.
- `tests/test_webhook_pipeline_service.py` expandido para validar persistencia de status/CRM em:
  - fluxo normal;
  - fluxo com guardrail;
  - short-circuit de duplicidade;
  - comando de sessao `reset`.
- `tests/test_lead_model.py` atualizado para contrato da coluna `status`.
- `tests/test_migration_contract.py` atualizado para validar migration da fase 7.5.
