# Fase 2 - Feature 2.2

## O que foi feito

- Implementada a funcao `load_prompt()` em `app/config.py`.
- Definida ordem de composicao dos arquivos de prompt:
  - `identity.md`
  - `departments.md`
  - `objections.md`
  - `faq.md`
  - `flow_steps.md`
- Carregamento padronizado com concatenacao em uma unica string.
- Erro explicito quando nenhum arquivo de prompt e encontrado.

## Estrutura inicial de prompts

- Criados arquivos base em `prompts/` para suportar a composicao modular.
- Cada arquivo ja inclui secoes em PT-BR para onboarding:
  - `## O QUE PREENCHER`
  - `## NAO ALTERAR`

## Testes da feature

- Criado `tests/test_prompt_loader.py` para validar:
  - ordem de concatenacao dos prompts;
  - falha clara quando nenhum arquivo existe.
