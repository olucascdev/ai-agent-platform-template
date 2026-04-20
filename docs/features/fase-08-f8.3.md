# Fase 8 - Feature 8.3

## O que foi feito

- Implementada politica de segredos em `app/security/secret_policy.py` para bloquear hardcodes em:
  - codigo da aplicacao (`app/`, `db/`);
  - workflows CI (`.github/workflows/`);
  - scripts operacionais (`scripts/`).
- Regras adicionadas para detectar:
  - atribuicao literal de variaveis sensiveis conhecidas (`OPENAI_API_KEY`, `CRM_TOKEN`, etc.);
  - valores literais de segredos em workflows;
  - padroes de tokens reais (ex.: `sk-*`, `ghp_*`, `AIza*`).
- Criado validador executavel `scripts/check_secrets_policy.py` para uso local/CI.
- Pipeline de validacao atualizado para enforcement automatico:
  - `.github/workflows/validate.yml` agora executa o check de segredos;
  - `scripts/validate.sh` atualizado com etapa de politica de segredos.

## Testes da feature

- Criado `tests/test_secret_policy.py` cobrindo:
  - deteccao de segredo hardcoded em workflow;
  - aceitacao de segredo via `${{ secrets.* }}`;
  - deteccao de segredo hardcoded em codigo;
  - garantia de que o repositorio atual nao viola a politica.
