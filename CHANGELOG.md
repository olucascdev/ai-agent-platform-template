# Changelog

Todas as mudancas notaveis neste projeto serao documentadas neste arquivo.

O formato e baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Em desenvolvimento
- Feature 10.4 - pipeline de release
- Feature 10.5 - documentacao final de operacao

## [1.0.0] - 2026-04-20

Primeira release publica do template conversacional Agno.

### Added

#### Fase 10 - Publicacao do template
- Checklist completo de pre-release com validacao automatizada
- Guia de onboarding para novo cliente (setup em < 30 min)
- Documentacao completa de configuracao e customizacao
- 5 exemplos de configuracao para diferentes cenarios
- Politica de versionamento semantico
- CHANGELOG.md com historico completo
- Processo documentado de release

#### Fase 09 - Template plugavel
- Arquitetura desacoplada de n8n (opcional por cliente)
- Fluxo direto: CRM/Canal → API → pipeline interno
- Integradores externos opcionais (n8n, iPaaS, etc.)

#### Fase 08 - Qualidade operacional e seguranca
- Logs estruturados em JSON com correlation ID
- Middleware de propagacao de X-Correlation-Id
- Handlers globais de erro com envelope padronizado
- Politica de segredos com varredura automatizada
- Cobertura minima de testes (85%) com pytest-cov
- Validacao de migrations no CI com Postgres dedicado

#### Fase 07 - Webhook completo e pipeline E2E
- Endpoint `POST /webhook/whatsapp` com schema validado
- Pipeline completo: normalizar → lead upsert → CRM → agente → sender
- Idempotencia por message_id/event_id
- Tratamento de comandos de sessao
- Persistencia de metadados (crm_contact_id, status)

#### Fase 06 - Orquestracao do agente
- AgentFactory com carregamento de prompts modulares
- Sessao single-client (AGENT_SESSION_PREFIX + telefone)
- Regras de FAQ, qualificacao e transferencia por departamento
- Geracao de comments estruturados para handoff humano
- Guardrails de resposta (limites, tom, proibicoes)

#### Fase 05 - Preprocessor multimodal
- Normalizador de evento canonico de entrada
- Transcricao de audio com provider configuravel (OpenAI, Groq)
- Analise de imagem com extracao textual/contextual
- Processamento de PDF
- Composer final de contexto para agente
- Fallback seguro para arquivos invalidos

#### Fase 04 - Integracoes HTTP
- HTTP client base resiliente (timeout, retry, logs seguros)
- CRMClient configuravel por env (Helena como default)
- WhatsAppSenderClient configuravel por env
- Politica de erro/retry para 429/5xx e erros terminais
- Contratos de request/response documentados

#### Fase 03 - Banco e lead service
- Estrategia de URL multi-provider (local/Supabase/Neon)
- SQLAlchemy async + modelo Lead
- Alembic + migration inicial leads
- LeadService com upsert idempotente e get_by_phone

#### Fase 02 - Configuracao central e prompts
- Settings centralizados com fail-fast
- load_prompt() com ordem de composicao definida

#### Fase 01 - Setup de repositorio e qualidade
- Dependencias pinadas no pyproject.toml
- .env.example padrao com variaveis obrigatorias
- Base de testes + CI (ruff, mypy, pytest)

#### Fase 00 - Limpeza do runtime base
- Remocao de agentes demo
- FastAPI base com /health endpoint
- Remocao de configs antigas sem uso

### Changed
- Nenhuma mudanca (primeira release)

### Deprecated
- Nenhuma deprecacao (primeira release)

### Removed
- Nenhuma remocao (primeira release)

### Fixed
- Nenhum fix (primeira release)

### Security
- Politica de segredos implementada
- Varredura automatica de tokens hardcoded
- Validacao de secrets no CI

## Formato de versao

Este projeto usa [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes que requerem acao do cliente
- **MINOR** (0.X.0): Novas features retrocompativeis
- **PATCH** (0.0.X): Bug fixes retrocompativeis

## Categorias de mudancas

- **Added**: Novas features
- **Changed**: Mudancas em features existentes
- **Deprecated**: Features que serao removidas em versoes futuras
- **Removed**: Features removidas
- **Fixed**: Bug fixes
- **Security**: Patches de seguranca

## Breaking Changes

Breaking changes sao sempre documentados com:
- Tag `[BREAKING]` no titulo da mudanca
- Descricao do impacto
- Guia de migracao

Exemplo:
```markdown
### Changed
- [BREAKING] Renomeado `CRM_TOKEN` para `CRM_API_TOKEN`
  - **Impacto**: Clientes precisam atualizar .env
  - **Migracao**: Renomeie a variavel no seu arquivo .env
```

## Como contribuir com o changelog

Ao adicionar uma feature ou fix:

1. Adicione entrada na secao `[Unreleased]`
2. Use a categoria apropriada (Added, Changed, Fixed, etc.)
3. Descreva a mudanca de forma clara e objetiva
4. Se for breaking change, adicione tag `[BREAKING]` e guia de migracao

## Links

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
