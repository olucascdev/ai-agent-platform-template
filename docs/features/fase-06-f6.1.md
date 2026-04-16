# Fase 6 - Feature 6.1

## O que foi feito

- Criado modulo `app/agent/factory.py` com a classe `AgentFactory` para centralizar a construcao do agente Agno.
- Implementado carregamento de prompts modulares no momento da criacao do agente usando `load_prompt()`.
- Definido builder padrao `build_default_openai_model()` para inicializar `OpenAIChat` com chave de API do ambiente.
- Adicionado helper `build_agent_factory()` para montar a factory com `settings` globais da aplicacao.
- Publicados exports de orquestracao em `app/agent/__init__.py` para facilitar uso nos proximos modulos da fase 6.
- Factory expandida para selecao de provider/modelo por ambiente (`chatgpt`, `openrouter`, `groq`, `claude`, `gemini`) sem alteracao de codigo.

## Testes da feature

- Criado `tests/test_agent_factory.py` cobrindo:
  - criacao de agente com prompt modular composto na ordem esperada;
  - propagacao de erro explicito quando nenhum arquivo de prompt existe;
  - contrato do helper `build_agent_factory()` com `settings` globais.
