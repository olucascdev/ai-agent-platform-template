# Fase 1 - Feature 1.3

## O que foi feito

- Preparada a base de testes com `pytest` e `pytest-asyncio` no `pyproject.toml`.
- Configurado o `pytest` para buscar automaticamente testes em `tests/`.
- Incluido teste assincrono de healthcheck para validar fluxo async da API.
- Atualizado o workflow de validacao para executar a suite de testes no CI.
- Atualizado script local `scripts/validate.sh` para incluir execucao de testes.

## Arquivos alterados

- `pyproject.toml`
- `.github/workflows/validate.yml`
- `scripts/validate.sh`
- `tests/test_health_async.py`
- `README.md`

## Testes da feature

- `pytest` agora executa testes sincronos e assincronos da base.
- O CI passa a validar formatacao, lint, tipagem e testes automaticamente.
