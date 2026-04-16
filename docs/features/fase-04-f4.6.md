# Fase 4 - Feature 4.6

## O que foi feito

- Criado `app/integrations/contracts.py` com camada de validacao de contrato HTTP em runtime.
- Adicionada excecao dedicada `IntegrationContractError` para erros de payload fora do contrato.
- Implementados utilitarios de parse:
  - `parse_json_payload()` para aceitar apenas `dict` ou `list`;
  - `parse_json_object_payload()` para operacoes que exigem objeto JSON.
- `CRMClient` atualizado para:
  - validar entradas obrigatorias (`phone`, `contact_id`, `department_id`, `comments`);
  - validar formato de resposta de lookup/transferencia com erros explicitos de contrato.
- `WhatsAppSenderClient` atualizado para:
  - validar entradas obrigatorias (`phone`, `text`);
  - validar tipo de payload retornado pelo sender.
- Exportados os novos contratos em `app/integrations/__init__.py`.

## Testes da feature

- Criado `tests/test_contracts.py` para validar parser de contrato HTTP e erros de formato.
- Expandido `tests/test_crm_client.py` com cenarios de:
  - validacao de parametros obrigatorios;
  - erro de contrato para payload invalido.
- Expandido `tests/test_whatsapp_sender_client.py` com cenarios de:
  - validacao de parametros obrigatorios;
  - erro de contrato para payload JSON primitivo.
