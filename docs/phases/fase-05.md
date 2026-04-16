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

## Proximas features da fase

- Feature 5.2 - transcricao de audio com provider configuravel.
- Feature 5.3 - analise de imagem (extracao textual/contextual).
- Feature 5.4 - processamento de PDF (quando aplicavel).
- Feature 5.5 - composer final de contexto para agente.
- Feature 5.6 - fallback seguro para falhas de midia/provider.
