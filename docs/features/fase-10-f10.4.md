# Feature 10.4 - pipeline de release

## Status

- Concluida.

## Objetivo

Automatizar processo de release no GitHub com workflow de criacao de tags, releases e validacao automatica pre-release.

## Contexto

O processo de release deve ser automatizado para:
- Reduzir erros humanos
- Garantir consistencia entre releases
- Validar qualidade antes de publicar
- Gerar release notes automaticamente
- Facilitar rollback se necessario

## Requisitos

### 1. Workflow de release automatizado

GitHub Actions workflow que:
- Valida pre-release check
- Cria tag automaticamente
- Gera release notes do CHANGELOG.md
- Publica release no GitHub
- Notifica equipe

### 2. Validacao pre-release

Antes de criar release:
- Executar todos testes
- Validar qualidade (ruff, mypy)
- Validar migrations
- Executar pre-release check
- Validar que versao foi atualizada

### 3. Release notes automaticas

Extrair release notes do CHANGELOG.md automaticamente.

### 4. Suporte a diferentes tipos de release

- Release normal (latest)
- Pre-release (beta, rc)
- Hotfix

## Implementacao

### 1. Criar workflow de release

`.github/workflows/release.yml` - Workflow principal de release

### 2. Criar workflow de pre-release check

`.github/workflows/pre-release.yml` - Validacao antes de release

### 3. Criar script de extracao de release notes

`scripts/extract_release_notes.py` - Extrai release notes do CHANGELOG.md

### 4. Documentar processo automatizado

Atualizar `docs/RELEASE_PROCESS.md` com processo automatizado.

## Criterios de aceitacao

- [x] `.github/workflows/release.yml` criado e funcional
- [x] `.github/workflows/pre-release.yml` criado e funcional
- [x] `scripts/extract_release_notes.py` criado
- [x] Documentacao atualizada em `docs/RELEASE_PROCESS.md`
- [x] Testes automatizados criados em `tests/test_release_pipeline.py`
- [x] Documentacao da feature concluida

## Testes

### Automatizados

- Validar que workflows existem e tem estrutura correta
- Validar que script de extracao funciona
- Validar que workflows tem jobs obrigatorios

### Manuais

- Criar release de teste (v1.0.1-test)
- Validar que workflow executa corretamente
- Validar que release notes sao geradas
- Validar que notificacao funciona

## Dependencias

- Feature 10.1 concluida (checklist de release)
- Feature 10.2 concluida (guia de onboarding)
- Feature 10.3 concluida (changelog e versionamento)

## Proximos passos

Apos conclusao desta feature:
- Feature 10.5 - documentacao final de operacao

## Tempo estimado

- Criacao de workflows: 2 horas
- Script de extracao: 30 minutos
- Testes: 1 hora
- Documentacao: 30 minutos
- Total: 4 horas
