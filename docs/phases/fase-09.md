# Fase 9 - template n8n oficial plugavel

## Status

- Em andamento.

## Features concluidas

### Feature 9.1 - workflow n8n base com credenciais/env vars

- Workflow base n8n criado para entrada WhatsApp e forwarding para API.
- Parametrizacao por env vars aplicada para URL base e timeout.
- Autenticacao baseada em credencial n8n (sem token hardcoded no workflow).
- Documentacao de setup adicionada para import em ambiente limpo.
- Cobertura automatizada adicionada para contrato estrutural e seguranca basica do JSON.

## Proximas features da fase

- Feature 9.2 - remover hardcodes de URL/token/session key fixa.
- Feature 9.3 - presets por cliente (Helena default).
- Feature 9.4 - documento "onde customizar" (CRM, sender, departamentos, prompts).
- Feature 9.5 - smoke test n8n -> API -> CRM/Sender.
