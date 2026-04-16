# Feature: limpeza do runtime base

## O que foi feito

- Removidos os agentes demo (`knowledge_agent` e `mcp_agent`) para evitar confusao no template.
- `app/main.py` foi simplificado para FastAPI puro com endpoint `/health`.
- Removido `app/config.yaml`, que era usado apenas para quick prompts dos agentes demo.
- Ajustado `pyproject.toml` para nao empacotar mais o namespace `agents*`.
- Adicionado teste automatizado para validar resposta do endpoint de health.

## Impacto

- O runtime deixa de depender do AgentOS demo e fica pronto para evolucao por fases do webhook conversacional.
- A base agora tem um ponto de verificacao minimo de disponibilidade da API.
