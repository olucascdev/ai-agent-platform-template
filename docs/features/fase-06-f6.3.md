# Fase 6 - Feature 6.3

## O que foi feito

- Criado modulo `app/agent/conversation_rules.py` com regras backend de conversa para:
  - deteccao de FAQ por palavras-chave;
  - qualificacao de lead (objetivo, orcamento e prazo);
  - decisao de transferencia para departamento.
- Definidos contratos tipados da feature:
  - `FaqResolution`;
  - `QualificationResult`;
  - `DepartmentTransferDecision`;
  - `ConversationRulesDecision`.
- Implementada funcao `evaluate_conversation_rules(message, department_ids=...)` para consolidar a decisao de intencao (`faq`, `qualification`, `transfer`, `general`).
- Adicionado catalogo padrao de departamentos com possibilidade de sobrescrita por mapa customizado em runtime.
- Exportados os contratos e avaliador em `app/agent/__init__.py` para uso nas proximas etapas da fase 6.

## Testes da feature

- Criado `tests/test_conversation_rules.py` cobrindo:
  - cenario de FAQ sem transferencia;
  - qualificacao parcial com pergunta de continuidade;
  - pedido explicito de humano com roteamento por departamento;
  - lead qualificado com transferencia comercial;
  - erro tecnico com roteamento para suporte;
  - erro explicito para mensagem vazia.
