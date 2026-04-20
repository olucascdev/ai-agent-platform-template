# Fase 8 - Feature 8.4

## O que foi feito

- Politica minima de cobertura automatizada definida no `pyproject.toml`.
- Dependencia `pytest-cov` adicionada no extra de desenvolvimento.
- Execucao de testes agora inclui cobertura por padrao via `pytest addopts`:
  - `--cov=app --cov=db`;
  - `--cov-report=term-missing`;
  - `--cov-fail-under=85`.
- Configuracao declarativa adicional adicionada em `tool.coverage`:
  - cobertura com branch habilitada;
  - `source = ["app", "db"]`;
  - `fail_under = 85` em `tool.coverage.report`.

## Testes da feature

- Criado `tests/test_coverage_policy.py` cobrindo:
  - presenca de `pytest-cov` no extra `dev`;
  - enforcement de `--cov-fail-under=85` nos `addopts` do pytest;
  - contrato declarativo de `fail_under` em `tool.coverage.report`.
