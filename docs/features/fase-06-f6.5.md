# Fase 6 - Feature 6.5

## O que foi feito

- Criado modulo `app/agent/guardrails.py` com guardrails de resposta para limites, tom e proibicoes.
- Implementada funcao `apply_response_guardrails()` para avaliar e transformar respostas antes do envio ao canal.
- Regras adicionadas:
  - bloqueio de resposta vazia com fallback seguro;
  - bloqueio de padroes proibidos (exposicao de token/credencial e linguagem ofensiva);
  - ajuste de tom para mensagens em caixa alta excessiva e pontuacao agressiva repetida;
  - limite de tamanho por caracteres com truncamento controlado.
- Definidos contratos tipados de resultado:
  - `GuardrailViolation`;
  - `GuardrailResult`.
- Exportados guardrails em `app/agent/__init__.py` para facilitar integracao na etapa de webhook/pipeline.

## Testes da feature

- Criado `tests/test_guardrails.py` cobrindo:
  - fallback em resposta vazia;
  - bloqueio por padrao de segredo;
  - normalizacao de tom;
  - truncamento por limite de tamanho;
  - fluxo seguro sem transformacao.
