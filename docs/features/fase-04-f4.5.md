# Fase 4 - Feature 4.5

## O que foi feito

- Fechado o contrato HTTP das integracoes da fase 4 em `docs/phases/contratos-http-fase-04.md`.
- Consolidado o documento com:
  - contrato de busca e transferencia do CRM;
  - contrato de envio de texto no sender WhatsApp;
  - matriz de autenticacao por header/prefixo;
  - politica de retry por tipo de integracao.
- Implementados testes de integracao simulada ponta a ponta em `tests/test_integrations_simulated.py`.
- Validado fluxo completo em ambiente mockado:
  1. lookup de contato no CRM;
  2. transferencia de contato no CRM;
  3. envio de mensagem no sender.
- Validado comportamento de retry especifico por integracao no cenario simulado:
  - CRM sem retry para `409`;
  - sender com retry para `425`.

## Testes da feature

- `tests/test_integrations_simulated.py`:
  - contrato HTTP ponta a ponta para CRM + sender;
  - diferenca de politica de retry por integracao.
