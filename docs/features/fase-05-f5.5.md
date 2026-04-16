# Fase 5 - Feature 5.5

## O que foi feito

- Criado modulo `app/preprocessing/message_composer.py` para composicao final da mensagem que sera enviada ao agente.
- Definidos contratos da feature:
  - `ComposedAgentInput`
  - `ComposerSource`
  - `MessageCompositionError`
- Implementada funcao `compose_agent_input()` com prioridade deterministica de fontes:
  1. `text` (mensagem original)
  2. `audio_transcription`
  3. `image_analysis`
  4. `pdf_processing`
- Implementado merge deterministico com:
  - bloco de mensagem principal (`[mensagem_principal]`);
  - bloco opcional de contexto complementar (`[contexto_complementar]`);
  - ordem fixa de fontes para evitar variacao de output.
- Adicionada validacao fail-fast para cenario sem texto util em nenhuma fonte.
- Exportados os contratos do composer em `app/preprocessing/__init__.py`.

## Testes da feature

- Criado `tests/test_message_composer.py` cobrindo:
  - prioridade de fonte com texto original disponivel;
  - fallback para audio quando texto nao existe;
  - prioridade imagem > pdf quando nao ha texto/audio;
  - fallback final para pdf;
  - limpeza de textos vazios/espacos;
  - erro quando nao existe conteudo textual util;
  - determinismo do output para mesma entrada.
