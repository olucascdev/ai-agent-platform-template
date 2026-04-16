# Fase 6 - orquestracao do agente

## Status

- Em andamento.

## Features concluidas

### Feature 6.1 - AgentFactory com carregamento de prompts modulares

- `AgentFactory` implementada para centralizar criacao de instancias do agente Agno.
- Prompt modular carregado via `load_prompt()` na construcao do agente.
- Builder padrao de modelo OpenAI adicionado para preparar base de execucao da conversa.
- Cobertura automatizada adicionada para contrato da factory e cenarios de erro de prompt.

### Feature 6.2 - sessao single-client (`AGENT_SESSION_PREFIX + telefone`)

- Helper de sessao implementado para compor `session_id` deterministico por cliente e telefone.
- Telefone normalizado para formato somente digitos, reduzindo risco de sessao duplicada por variacao de mascara.
- `AgentFactory` expandida com `build_for_phone()` para iniciar agente com sessao derivada automaticamente.
- Cobertura automatizada adicionada para contrato de composicao de sessao e validacoes de entrada.

### Feature 6.3 - regras de FAQ, qualificacao e transferencia por departamento

- Regras de conversa backend implementadas para identificar FAQ, qualificacao e necessidade de handoff.
- Avaliador unico (`evaluate_conversation_rules`) consolidando intencao e decisao de transferencia.
- Qualificacao estruturada por sinais de objetivo, orcamento e prazo, com pergunta de continuidade para lacunas.
- Roteamento de transferencia para departamentos por regra (humano, financeiro, suporte e comercial).
- Cobertura automatizada adicionada para cenarios de FAQ, qualificacao e pedido de humano.

## Proximas features da fase

- Feature 6.4 - geracao de comments estruturados para handoff humano.
- Feature 6.5 - guardrails de resposta (limites, tom, proibicoes).
