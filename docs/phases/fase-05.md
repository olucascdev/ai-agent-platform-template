# Fase 5 - preprocessor multimodal

## Status

- Em andamento.

## Features concluidas

### Feature 5.1 - normalizador de evento canonico

- `normalize_incoming_event()` implementada para converter payload bruto em contrato interno previsivel.
- Suporte adicionado para entrada com/sem wrapper `body`.
- Classificacao de tipo de entrada implementada (`text`, `audio`, `image`, `pdf`, `other`).
- Deduplicacao de anexos e validacao de campos obrigatorios aplicadas.
- Cobertura automatizada adicionada para cenarios principais e de erro.

### Feature 5.2 - transcricao de audio com provider configuravel

- Fluxo de transcricao de audio implementado com selecao de provider via configuracao.
- Provider OpenAI implementado com suporte a model/language configuraveis.
- Validacoes fail-fast adicionadas para anexo de audio ausente ou sem URL valida.
- Erros de download/transcricao mapeados para excecoes de dominio da feature.
- Cobertura automatizada adicionada para contrato do provider e cenarios de falha.

## Proximas features da fase

- Feature 5.3 - analise de imagem (extracao textual/contextual).
- Feature 5.4 - processamento de PDF (quando aplicavel).
- Feature 5.5 - composer final de contexto para agente.
- Feature 5.6 - fallback seguro para falhas de midia/provider.
