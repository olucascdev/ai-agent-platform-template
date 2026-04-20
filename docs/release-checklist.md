# Checklist de Release - Template Conversacional Agno

Este documento contem o checklist completo de validacao pre-release. Todos os itens devem ser verificados antes de publicar uma nova versao do template.

## Como usar este checklist

1. Execute o script automatizado: `python scripts/pre_release_check.py`
2. Valide manualmente os itens que nao podem ser automatizados
3. Marque cada item concluido com `[x]`
4. Apenas publique a release quando todos os itens estiverem marcados

---

## 1. Qualidade de Codigo

### Automatizado

- [ ] `uv run ruff check .` passa sem erros
- [ ] `uv run mypy .` passa sem erros de tipo
- [ ] `uv run pytest` passa com cobertura >= 85%

### Manual

- [ ] Nenhum TODO/FIXME critico pendente no codigo
- [ ] Code review realizado (se aplicavel)
- [ ] Nenhum comentario de debug ou print statement esquecido

---

## 2. Seguranca

### Automatizado

- [ ] `python scripts/check_secrets_policy.py` passa sem violacoes
- [ ] `.env.example` existe e esta atualizado
- [ ] `.gitignore` protege arquivos sensiveis

### Manual

- [ ] Nenhum token/senha hardcoded em codigo
- [ ] Nenhum token/senha hardcoded em workflows
- [ ] Nenhuma credencial real commitada no historico do git
- [ ] Variaveis sensiveis documentadas no `.env.example` (sem valores reais)
- [ ] Secrets do GitHub Actions configurados corretamente (se aplicavel)

---

## 3. Banco de Dados

### Automatizado

- [ ] Migration files existem em `db/migrations/versions/`

### Manual

- [ ] `alembic upgrade head` executa sem erro
- [ ] `alembic downgrade -1` funciona corretamente
- [ ] `alembic upgrade head` (re-upgrade) funciona
- [ ] Nenhuma migration com conflito ou dependencia quebrada
- [ ] Migrations testadas em ambiente limpo (banco vazio)
- [ ] Schema do banco documentado (se necessario)

---

## 4. Documentacao

### Automatizado

- [ ] `README.md` existe
- [ ] `docs/phases/fase-10.md` existe
- [ ] `.env.example` existe
- [ ] Features documentadas em `docs/features/`

### Manual

- [ ] `README.md` atualizado com instrucoes claras de setup
- [ ] Todas features implementadas documentadas em `docs/features/`
- [ ] Todas fases concluidas documentadas em `docs/phases/`
- [ ] Contratos HTTP documentados (request/response)
- [ ] Variaveis de ambiente documentadas com descricao e exemplos
- [ ] Guia de troubleshooting atualizado (se aplicavel)
- [ ] Changelog atualizado com mudancas da versao
- [ ] Breaking changes documentados claramente

---

## 5. Build e Deploy

### Automatizado

- [ ] `pyproject.toml` existe
- [ ] `Dockerfile` existe
- [ ] `compose.yaml` existe

### Manual

- [ ] `docker compose up --build` sobe sem erros
- [ ] Health endpoint responde: `GET /health` retorna 200
- [ ] API docs acessivel: `http://localhost:8000/docs`
- [ ] Nenhuma dependencia faltando no `pyproject.toml`
- [ ] Versoes de dependencias pinadas corretamente
- [ ] Build do Docker completa em tempo razoavel (< 5 min)
- [ ] Imagem Docker tem tamanho razoavel (< 1GB se possivel)

---

## 6. Integracao

### Automatizado

- [ ] `app/api/webhook.py` existe
- [ ] `app/integrations/crm_client.py` existe
- [ ] `app/integrations/whatsapp_sender_client.py` existe
- [ ] `app/preprocessing/event_normalizer.py` existe

### Manual

- [ ] Webhook aceita payload valido: `POST /webhook/whatsapp`
- [ ] Idempotencia funciona (mesmo event_id nao duplica processamento)
- [ ] CRM client configuravel por env vars (sem hardcode)
- [ ] Sender client configuravel por env vars (sem hardcode)
- [ ] Preprocessor multimodal funciona:
  - [ ] Texto
  - [ ] Audio (transcricao)
  - [ ] Imagem (analise)
  - [ ] PDF (processamento)
- [ ] Tratamento de erro gracioso em todas integracoes
- [ ] Retry policy funciona para erros temporarios (429, 5xx)

---

## 7. CI/CD

### Automatizado

- [ ] `.github/workflows/validate.yml` existe

### Manual

- [ ] Workflow `.github/workflows/validate.yml` passa no GitHub
- [ ] Todos jobs do CI executam com sucesso:
  - [ ] Lint (ruff)
  - [ ] Type check (mypy)
  - [ ] Tests (pytest)
  - [ ] Secrets policy
  - [ ] Migrations validation
- [ ] Branch protection configurada (se aplicavel)
- [ ] Status checks obrigatorios configurados (se aplicavel)

---

## 8. Template

### Automatizado

- [ ] `app/config.py` existe (configuracao centralizada)

### Manual

- [ ] Nenhum hardcode especifico de cliente
- [ ] Helena configurada como default (mas configuravel)
- [ ] Prompts modulares e versionados
- [ ] Configuracao centralizada em `app/config.py`
- [ ] Facil trocar CRM apenas por env vars:
  - [ ] `CRM_BASE_URL`
  - [ ] `CRM_API_TOKEN`
  - [ ] `CRM_TIMEOUT`
- [ ] Facil trocar Sender apenas por env vars:
  - [ ] `WHATSAPP_SENDER_BASE_URL`
  - [ ] `WHATSAPP_SENDER_API_TOKEN`
- [ ] Facil trocar provider de modelo:
  - [ ] `AGENT_MODEL_PROVIDER`
  - [ ] `AGENT_MODEL_ID`
  - [ ] `AGENT_MODEL_API_KEY`
- [ ] Template pode ser replicado para novo cliente em < 1 hora

---

## 9. Testes E2E

### Manual

- [ ] Fluxo completo testado: webhook -> lead upsert -> CRM -> agente -> sender
- [ ] Cenario de FAQ testado
- [ ] Cenario de qualificacao testado
- [ ] Cenario de transferencia para humano testado
- [ ] Cenario de erro temporario (retry) testado
- [ ] Cenario de erro permanente (graceful failure) testado
- [ ] Idempotencia validada com evento duplicado

---

## 10. Performance e Observabilidade

### Manual

- [ ] Logs estruturados funcionando
- [ ] Correlation ID propagado em todos logs
- [ ] Metricas de latencia aceitaveis (< 2s para texto simples)
- [ ] Nenhum memory leak detectado
- [ ] Nenhum connection pool leak detectado
- [ ] Tratamento de timeout configurado em todas integracoes

---

## 11. Onboarding

### Manual

- [ ] Guia de onboarding criado e testado
- [ ] Novo desenvolvedor consegue subir o projeto em < 30 min
- [ ] Documentacao de customizacao clara
- [ ] Exemplos de configuracao por provider documentados
- [ ] FAQ de troubleshooting atualizado

---

## 12. Release

### Manual

- [ ] Versao definida seguindo semantic versioning (ex: 1.0.0)
- [ ] Tag git criada com a versao
- [ ] CHANGELOG.md atualizado
- [ ] Release notes preparadas
- [ ] Breaking changes comunicados claramente
- [ ] Migration path documentado (se houver breaking changes)

---

## Validacao Final

### Automatizado

- [ ] `python scripts/pre_release_check.py` passa 100%

### Manual

- [ ] Dry-run de onboarding em ambiente completamente novo
- [ ] Confirmacao de que todos itens acima estao marcados
- [ ] Aprovacao de pelo menos um revisor (se aplicavel)
- [ ] Comunicacao de release preparada para stakeholders

---

## Pos-Release

Apos publicar a release, validar:

- [ ] Release publicada no GitHub
- [ ] Tag criada corretamente
- [ ] Release notes visiveis
- [ ] Documentacao acessivel
- [ ] Template pode ser clonado e usado imediatamente

---

## Notas

- Este checklist deve ser revisado e atualizado a cada release
- Itens marcados como "Automatizado" sao validados pelo script `pre_release_check.py`
- Itens marcados como "Manual" requerem validacao humana
- Nao pule nenhum item - todos sao importantes para qualidade do template

## Contato

Para duvidas sobre o checklist ou processo de release, consulte a documentacao em `docs/phases/fase-10.md`.
