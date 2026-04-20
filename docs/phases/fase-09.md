# Fase 9 - template plugavel sem dependencia obrigatoria de n8n

## Status

- Em andamento.

## Features concluidas

### Feature 9.1 - workflow n8n base com credenciais/env vars

- Arquitetura oficial definida como fluxo direto: CRM/Canal -> API (`POST /webhook/whatsapp`) -> pipeline interno.
- n8n removido do caminho obrigatorio do runtime para evitar complexidade e latencia extra.
- Integradores externos passam a ser opcionais por cliente, nao requisito do template Agno.

## Proximas features da fase

- Feature 9.2 - remover hardcodes de URL/token/session key fixa.
- Feature 9.3 - presets por cliente (Helena default).
- Feature 9.4 - documento "onde customizar" (CRM, sender, departamentos, prompts).
- Feature 9.5 - smoke test CRM/Canal -> API -> CRM/Sender (sem dependencia obrigatoria de n8n).
