# Fase 5 - Feature 5.6

## O que foi feito

- Criado modulo `app/preprocessing/fallback_pipeline.py` para orquestracao resiliente do preprocessor multimodal.
- Implementado `preprocess_event_with_fallback()` com estrategia de fallback seguro quando midia/provider falhar.
- Definidos contratos da feature:
  - `PreprocessingIssue`
  - `ResilientPreprocessingResult`
  - `PreprocessingStage`
- Comportamento implementado:
  - tentativas de processamento por tipo de midia (audio, imagem, pdf);
  - captura de falhas por etapa sem derrubar o fluxo;
  - composicao normal quando houver conteudo textual util;
  - fallback textual seguro quando composicao final nao for possivel.
- Implementada mensagem de fallback padrao configuravel por ambiente (`media_failure_fallback_text`).
- Exportados contratos e orquestrador resiliente em `app/preprocessing/__init__.py`.
- Adicionadas configuracoes no `Settings`:
  - `media_failure_fallback_text`.
- Atualizado `.env.example` com variavel opcional da feature.

## Testes da feature

- Criado `tests/test_preprocessing_fallback.py` cobrindo:
  - fluxo textual normal sem fallback;
  - falha de audio com texto disponivel (sem quebrar fluxo);
  - falha de midia sem texto com ativacao de fallback seguro;
  - cenario misto (imagem sucesso + pdf falha);
  - rastreabilidade de artefatos multimodais de sucesso.
- Expandido `tests/test_config.py` para validar default de `media_failure_fallback_text`.
