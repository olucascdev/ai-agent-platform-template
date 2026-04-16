# Fase 2 - configuracao central

## Status

- Em andamento.

## Features concluidas

### Feature 2.1 - settings centralizados com fail-fast

- `app/config.py` implementado com `pydantic-settings`.
- Variaveis obrigatorias validadas na inicializacao da aplicacao.
- Testes adicionados para defaults e campos obrigatorios.

### Feature 2.2 - composicao modular de prompts

- `load_prompt()` implementada em `app/config.py`.
- Ordem de leitura dos arquivos de `prompts/` definida e validada.
- Erro explicito adicionado para ausencia total de arquivos de prompt.
- Testes adicionados para ordem e falha de carregamento.

## Proximas features da fase

- Nenhuma. Fase 2 finalizada.
