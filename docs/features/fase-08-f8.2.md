# Fase 8 - Feature 8.2

## O que foi feito

- Criado padrao global de erro HTTP em `app/api/errors.py` com handlers para:
  - erros de aplicacao (`ApiApplicationError`);
  - validacao de request (`RequestValidationError`);
  - erros HTTP (`404`, `405`, etc.);
  - excecoes inesperadas (`500`).
- Definido envelope auditavel de erro em `app/models/error.py` com campos obrigatorios:
  - `code`, `message`, `error_type`;
  - `correlation_id`, `path`, `method`, `ts`;
  - `details` opcional para diagnostico.
- Registro de handlers globais integrado no bootstrap da API em `app/main.py`.
- Endpoint de webhook ajustado para converter falhas de normalizacao em erro de dominio (`webhook.normalization_error`) mantendo padrao unico de resposta.
- Logs estruturados de erro (`api_error_response`) adicionados para observabilidade e auditoria.

## Testes da feature

- Criado `tests/test_api_error_contract.py` cobrindo:
  - envelope padrao para erro de validacao (`422`);
  - envelope padrao para erro de aplicacao (`webhook.normalization_error`);
  - envelope padrao para erro inesperado (`500`) sem vazamento de detalhe interno;
  - envelope padrao para rota inexistente (`404`).
