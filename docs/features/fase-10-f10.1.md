# Feature 10.1 - checklist de release

## Status

- Concluida.

## Objetivo

Criar checklist completo de validacao pre-release para garantir que o template esta pronto para publicacao e replicacao por cliente.

## Contexto

A fase 10 finaliza o template conversacional para publicacao no GitHub. Esta feature estabelece os criterios minimos que devem ser validados antes de qualquer release, garantindo qualidade, seguranca e documentacao adequada.

## Requisitos

### Checklist de validacao pre-release

#### 1. Qualidade de codigo

- [ ] `uv run ruff check .` passa sem erros
- [ ] `uv run mypy .` passa sem erros de tipo
- [ ] `uv run pytest` passa com cobertura >= 85%
- [ ] Nenhum TODO/FIXME critico pendente no codigo

#### 2. Seguranca

- [ ] `python scripts/check_secrets_policy.py` passa sem violacoes
- [ ] Nenhum token/senha hardcoded em codigo ou workflows
- [ ] `.env.example` atualizado com todas variaveis obrigatorias
- [ ] `.gitignore` protege arquivos sensiveis (`.env`, credenciais, etc.)

#### 3. Banco de dados

- [ ] Migrations executam sem erro: `alembic upgrade head`
- [ ] Downgrade funciona: `alembic downgrade -1`
- [ ] Re-upgrade funciona: `alembic upgrade head`
- [ ] Nenhuma migration com conflito ou dependencia quebrada

#### 4. Documentacao

- [ ] `README.md` atualizado com instrucoes claras de setup
- [ ] Todas features documentadas em `docs/features/`
- [ ] Todas fases documentadas em `docs/phases/`
- [ ] Contratos HTTP documentados (request/response)
- [ ] Variaveis de ambiente documentadas

#### 5. Build e deploy

- [ ] `docker compose up --build` sobe sem erros
- [ ] Health endpoint responde: `GET /health` retorna 200
- [ ] API docs acessivel: `http://localhost:8000/docs`
- [ ] Nenhuma dependencia faltando no `pyproject.toml`

#### 6. Integracao

- [ ] Webhook aceita payload valido: `POST /webhook/whatsapp`
- [ ] Idempotencia funciona (mesmo event_id nao duplica)
- [ ] CRM client configuravel por env vars
- [ ] Sender client configuravel por env vars
- [ ] Preprocessor multimodal funciona (texto/audio/imagem/pdf)

#### 7. CI/CD

- [ ] Workflow `.github/workflows/validate.yml` passa
- [ ] Todos jobs do CI executam com sucesso
- [ ] Validacao de migrations no CI funciona
- [ ] Politica de segredos validada no CI

#### 8. Template

- [ ] Nenhum hardcode especifico de cliente (Helena como default configuravel)
- [ ] Prompts modulares e versionados
- [ ] Configuracao centralizada em `app/config.py`
- [ ] Facil trocar CRM/Sender apenas por env vars

## Implementacao

### Script de validacao pre-release

Criar script automatizado que executa todos os checks do checklist:

```python
# scripts/pre_release_check.py
"""
Script de validacao pre-release.
Executa todos os checks obrigatorios antes de publicar uma release.
"""
```

### Documento de checklist

Criar documento markdown com checklist interativo para validacao manual:

```markdown
# docs/release-checklist.md
```

## Criterios de aceitacao

- [x] Script `scripts/pre_release_check.py` criado e funcional
- [x] Documento `docs/release-checklist.md` criado com checklist completo
- [x] Testes automatizados criados em `tests/test_pre_release_check.py`
- [x] Documentacao da feature concluida em `docs/features/fase-10-f10.1.md`

## Testes

### Automatizados

- Teste do script de pre-release check
- Validacao de que todos gates de qualidade estao configurados

### Manuais

- Executar checklist completo em ambiente limpo
- Validar que nenhum item critico esta pendente
- Confirmar que template pode ser replicado por novo cliente

## Dependencias

- Fase 08 concluida (qualidade operacional)
- Fase 09 concluida (template plugavel)

## Proximos passos

Apos conclusao desta feature:
- Feature 10.2 - guia de onboarding por cliente
- Feature 10.3 - changelog e versionamento
- Feature 10.4 - pipeline de release
- Feature 10.5 - documentacao final de operacao
