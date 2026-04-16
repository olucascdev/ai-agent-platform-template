# Fase 4 - Feature 4.3

## O que foi feito

- Criado `app/integrations/whatsapp_sender_client.py` com cliente de envio WhatsApp configuravel via HTTP.
- Implementada classe `WhatsAppSenderClient` com metodo `send_text(phone, text)`.
- Implementada classe `WhatsAppSendResult` para padronizar retorno de envio (`status_code` + payload).
- Adicionada factory `build_whatsapp_sender_client()` com configuracao centralizada de ambiente.
- Adicionado helper de parse de URL completa do sender (`_split_sender_url`) para separar base URL e path com query.
- Tornados configuraveis via settings:
  - metodo HTTP (`whatsapp_sender_method`);
  - chaves de payload (`whatsapp_sender_number_field`, `whatsapp_sender_text_field`);
  - cabecalho de autenticacao (`whatsapp_sender_auth_header_name`, `whatsapp_sender_auth_header_prefix`).
- Atualizados exports do pacote de integracoes em `app/integrations/__init__.py`.
- Atualizado `.env.example` com bloco opcional de customizacao do sender.

## Testes da feature

- Criado `tests/test_whatsapp_sender_client.py` cobrindo:
  - envio com contrato padrao (`number`/`text`);
  - contrato customizado (metodo e campos de payload);
  - resposta sem corpo (payload vazio);
  - parse de URL com query;
  - erro claro para URL invalida;
  - montagem via settings com header customizado sem prefixo (ex.: `token`).
- Expandido `tests/test_config.py` para validar defaults das novas configuracoes de sender.
