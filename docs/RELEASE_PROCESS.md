# Processo de Release - Template Conversacional Agno

Este documento descreve o processo completo para criar uma nova release do template.

## Indice

- [Pre-requisitos](#pre-requisitos)
- [Tipos de Release](#tipos-de-release)
- [Processo Manual](#processo-manual)
- [Processo Automatizado (Recomendado)](#processo-automatizado-recomendado)
- [Checklist de Release](#checklist-de-release)
- [Rollback](#rollback)
- [Comunicacao](#comunicacao)

---

## Pre-requisitos

Antes de iniciar uma release:

1. **Todas features planejadas estao concluidas**
2. **Todos testes passam**: `pytest`
3. **Qualidade validada**: `ruff check .` e `mypy .`
4. **Migrations testadas**: `alembic upgrade head`
5. **Documentacao atualizada**
6. **Checklist de pre-release aprovado**: `python scripts/pre_release_check.py`

---

## Tipos de Release

Seguimos [Semantic Versioning 2.0.0](https://semver.org/):

### PATCH (0.0.X)

Bug fixes retrocompativeis.

**Exemplos**:
- Correcao de bug em validacao
- Fix de typo em mensagem de erro
- Correcao de documentacao

**Quando usar**: Apenas bug fixes, sem novas features.

### MINOR (0.X.0)

Novas features retrocompativeis.

**Exemplos**:
- Nova integracao com provider
- Novo preprocessor de midia
- Nova feature opcional

**Quando usar**: Adicao de funcionalidade sem quebrar compatibilidade.

### MAJOR (X.0.0)

Breaking changes que requerem acao do cliente.

**Exemplos**:
- Mudanca de schema de banco
- Remocao de variavel de ambiente
- Mudanca de contrato de API

**Quando usar**: Mudancas que quebram compatibilidade com versao anterior.

---

## Processo Automatizado (Recomendado)

O template possui pipeline automatizado de release via GitHub Actions. Este e o metodo recomendado.

### Visao geral

1. Atualizar versao e CHANGELOG
2. Criar PR para main
3. Workflow valida automaticamente
4. Merge do PR
5. Criar e push da tag
6. Workflow cria release automaticamente

### Passo a passo automatizado

#### 1. Criar branch de release

```bash
git checkout main
git pull origin main
git checkout -b release/v1.2.3
```

#### 2. Atualizar versao

```bash
python scripts/bump_version.py patch  # ou minor, major
```

Isso atualiza automaticamente:
- `VERSION`
- `pyproject.toml`
- `CHANGELOG.md` (adiciona secao para nova versao)

#### 3. Editar CHANGELOG.md

Adicione detalhes da release na secao criada:

```markdown
## [1.2.3] - 2026-04-20

### Added
- Nova feature X

### Fixed
- Bug Y corrigido
```

#### 4. Commit e push

```bash
git add VERSION pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"
git push origin release/v1.2.3
```

#### 5. Criar Pull Request

Crie PR de `release/v1.2.3` para `main`.

O workflow **pre-release.yml** sera acionado automaticamente e vai:
- ✅ Validar consistencia de versao (VERSION vs pyproject.toml)
- ✅ Validar que CHANGELOG.md foi atualizado
- ✅ Validar formato da versao
- ✅ Executar pre-release check completo
- 💬 Comentar no PR com resultado

#### 6. Review e merge

Aguarde aprovacao do CI e merge para `main`.

#### 7. Criar e push tag

```bash
git checkout main
git pull origin main
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

#### 8. Release automatica

O workflow **release.yml** sera acionado automaticamente e vai:
- ✅ Executar validacoes completas (lint, type check, tests, secrets)
- 📝 Extrair release notes do CHANGELOG.md
- 🚀 Criar release no GitHub
- 📢 Notificar resultado

A release estara disponivel em: `https://github.com/[org]/[repo]/releases/tag/v1.2.3`

### Vantagens do processo automatizado

- ✅ Validacao automatica antes de release
- ✅ Release notes geradas automaticamente
- ✅ Menos erros humanos
- ✅ Processo consistente
- ✅ Rastreabilidade completa
- ✅ Rollback facilitado

---

## Processo Manual

Se preferir criar release manualmente (nao recomendado):

### 1. Preparacao

#### 1.1. Criar branch de release

```bash
git checkout main
git pull origin main
git checkout -b release/v1.2.3
```

#### 1.2. Executar checklist de pre-release

```bash
python scripts/pre_release_check.py
```

Todos os checks devem passar antes de continuar.

#### 1.3. Validar testes

```bash
pytest --cov=app --cov=db --cov-fail-under=85
```

### 2. Atualizacao de versao

#### 2.1. Bump de versao

Para **patch** (1.0.0 → 1.0.1):
```bash
python scripts/bump_version.py patch
```

Para **minor** (1.0.0 → 1.1.0):
```bash
python scripts/bump_version.py minor
```

Para **major** (1.0.0 → 2.0.0):
```bash
python scripts/bump_version.py major
```

Para versao especifica:
```bash
python scripts/bump_version.py 1.2.3
```

O script atualiza automaticamente:
- `VERSION`
- `pyproject.toml`
- `CHANGELOG.md`

#### 2.2. Atualizar CHANGELOG.md

Edite `CHANGELOG.md` e adicione detalhes da release na secao criada:

```markdown
## [1.2.3] - 2026-04-20

### Added
- Nova feature X que permite Y
- Suporte para provider Z

### Changed
- Melhorado performance de processamento de audio

### Fixed
- Corrigido bug em idempotencia de webhook
- Corrigido timeout em requisicoes ao CRM

### Security
- Atualizado dependencia X para versao segura
```

Se houver **breaking changes**, documente claramente:

```markdown
### Changed
- [BREAKING] Renomeado `CRM_TOKEN` para `CRM_API_TOKEN`
  - **Impacto**: Clientes precisam atualizar .env
  - **Migracao**: Renomeie a variavel no seu arquivo .env
  - **Exemplo**: `CRM_TOKEN=abc` → `CRM_API_TOKEN=abc`
```

### 3. Commit e tag

#### 3.1. Commit das mudancas

```bash
git add VERSION pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"
```

#### 3.2. Criar tag

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
```

#### 3.3. Push

```bash
git push origin release/v1.2.3
git push origin v1.2.3
```

### 4. Pull Request

#### 4.1. Criar PR

Crie Pull Request de `release/v1.2.3` para `main` com:

**Titulo**: `Release v1.2.3`

**Descricao**:
```markdown
## Release v1.2.3

### Resumo
Breve descricao das principais mudancas desta release.

### Mudancas
- Feature X adicionada
- Bug Y corrigido
- Performance melhorada em Z

### Breaking Changes
- Nenhum (ou listar se houver)

### Checklist
- [x] Pre-release check passou
- [x] Todos testes passam
- [x] CHANGELOG.md atualizado
- [x] Documentacao atualizada
- [x] Tag criada
```

#### 4.2. Review e merge

1. Solicite review de pelo menos um desenvolvedor
2. Aguarde aprovacao do CI
3. Merge para `main`

### 5. Publicacao no GitHub

#### 5.1. Criar release no GitHub

1. Va para: `https://github.com/[org]/[repo]/releases/new`
2. Selecione a tag: `v1.2.3`
3. Titulo: `v1.2.3`
4. Descricao: Copie do CHANGELOG.md

**Template de release notes**:

```markdown
## What's Changed

### Added
- Nova feature X que permite Y
- Suporte para provider Z

### Changed
- Melhorado performance de processamento de audio

### Fixed
- Corrigido bug em idempotencia de webhook
- Corrigido timeout em requisicoes ao CRM

### Security
- Atualizado dependencia X para versao segura

## Breaking Changes

Nenhum (ou listar se houver)

## Upgrade Guide

Para atualizar de v1.2.2 para v1.2.3:

1. Pull da nova versao: `git pull origin main`
2. Atualizar dependencias: `uv sync`
3. Executar migrations: `alembic upgrade head`
4. Reiniciar servicos: `docker compose restart`

## Full Changelog

https://github.com/[org]/[repo]/compare/v1.2.2...v1.2.3
```

5. Marque como **latest release** (se for a mais recente)
6. Publique

### 6. Validacao pos-release

#### 6.1. Validar tag

```bash
git fetch --tags
git tag -l | grep v1.2.3
```

#### 6.2. Validar release no GitHub

Acesse: `https://github.com/[org]/[repo]/releases/tag/v1.2.3`

#### 6.3. Testar instalacao limpa

```bash
git clone <repo-url>
cd <repo>
git checkout v1.2.3
cp .env.example .env
# Editar .env
docker compose up -d
curl http://localhost:8000/health
```

---

## Checklist de Release

Use este checklist para cada release:

### Pre-release
- [ ] Todas features planejadas concluidas
- [ ] Todos testes passam
- [ ] Pre-release check passou
- [ ] Documentacao atualizada
- [ ] CHANGELOG.md preparado

### Release
- [ ] Branch de release criada
- [ ] Versao atualizada (VERSION, pyproject.toml, CHANGELOG.md)
- [ ] Commit criado
- [ ] Tag criada
- [ ] Push realizado
- [ ] PR criado e aprovado
- [ ] Merge para main

### Pos-release
- [ ] Release publicada no GitHub
- [ ] Release notes completas
- [ ] Tag validada
- [ ] Instalacao limpa testada
- [ ] Comunicacao enviada (se aplicavel)

---

## Rollback

Se houver problema critico apos release:

### Rollback rapido (recomendado)

1. **Criar hotfix**:
   ```bash
   git checkout v1.2.2  # Versao anterior estavel
   git checkout -b hotfix/v1.2.3-fix
   # Aplicar fix
   git commit -m "fix: critical bug in v1.2.3"
   ```

2. **Criar nova release** (patch):
   ```bash
   python scripts/bump_version.py patch  # 1.2.3 -> 1.2.4
   git tag -a v1.2.4 -m "Hotfix v1.2.4"
   git push origin hotfix/v1.2.3-fix
   git push origin v1.2.4
   ```

### Rollback completo (ultimo recurso)

1. **Deletar tag**:
   ```bash
   git tag -d v1.2.3
   git push origin :refs/tags/v1.2.3
   ```

2. **Deletar release no GitHub**:
   - Acesse releases
   - Delete a release v1.2.3

3. **Reverter commit**:
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

---

## Comunicacao

### Comunicacao interna

Apos release, notifique a equipe:

**Canal**: Slack/Discord/Email

**Template**:
```
🚀 Release v1.2.3 publicada!

Principais mudancas:
- Feature X adicionada
- Bug Y corrigido
- Performance melhorada

Breaking changes: Nenhum

Documentacao: https://github.com/[org]/[repo]/releases/tag/v1.2.3
```

### Comunicacao para clientes

Se houver breaking changes ou features importantes:

**Template de email**:
```
Assunto: Template Agno v1.2.3 - Nova versao disponivel

Ola,

Lancamos a versao 1.2.3 do template conversacional Agno com melhorias importantes:

NOVIDADES:
- Feature X que permite Y
- Suporte para provider Z

CORRECOES:
- Bug em idempotencia corrigido
- Performance melhorada

BREAKING CHANGES:
- Nenhum (ou listar se houver)

COMO ATUALIZAR:
1. git pull origin main
2. uv sync
3. alembic upgrade head
4. docker compose restart

Documentacao completa: [link]

Duvidas? Entre em contato.
```

---

## Recursos

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

## Contato

Para duvidas sobre o processo de release, consulte:
- Documentacao em `docs/`
- Checklist de release em `docs/release-checklist.md`
- Equipe de desenvolvimento
