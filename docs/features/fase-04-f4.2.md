# Fase 4 - Feature 4.2

## O que foi feito

- Criado `app/integrations/crm_client.py` com cliente CRM configuravel para:
  - busca de contato por telefone (`find_contact_by_phone`);
  - transferencia de contato para departamento (`transfer_contact`).
- Implementada classe `CRMContact` para padronizar retorno de lookup.
- Implementada factory `build_crm_client()` para montar o cliente com configuracoes centralizadas de `app/config.py`.
- Adicionados parametros de configuracao no `Settings`:
  - `crm_contacts_lookup_path`
  - `crm_lookup_phone_param`
  - `crm_lookup_phone_value_template`
  - `crm_lookup_service_id_param`
  - `crm_service_id`
  - `crm_transfer_path_template`
  - `crm_auth_header_name`
  - `crm_auth_header_prefix`
- Mantida compatibilidade com diferentes formatos de payload de contato (objeto unico ou lista em `data`).
- Atualizado `.env.example` com bloco de parametros opcionais para contratos de CRM diferentes.

## Testes da feature

- Criado `tests/test_crm_client.py` cobrindo:
  - lookup com parametros customizados de query (incluindo `serviceId`);
  - retorno `None` quando nao encontra contato;
  - compatibilidade com payload de objeto unico;
  - transferencia para departamento com payload esperado.
- Atualizado `tests/test_config.py` para validar defaults de configuracao do cliente CRM.
