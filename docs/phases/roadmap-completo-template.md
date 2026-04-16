# Roadmap completo do template conversacional (single-client)

## Escopo e premissas

- Este projeto e um template base por cliente (nao multi-tenancy em runtime).
- Fases 1, 2 e 3 ja foram validadas automaticamente e manualmente.
- O fluxo n8n atual serve como referencia funcional, mas com integracoes HTTP configuraveis por cliente.
- Nodes especificos de Digisac nao sao contrato fixo do template; o template deve aceitar CRM/Sender por URL e token configuraveis.

## Status geral atual

- Fase 00: concluida
- Fase 01: concluida
- Fase 02: concluida
- Fase 03: concluida
- Fase 04 em diante: planejadas neste documento

---

## Fase 00 - limpeza do runtime base

## Objetivo

Remover componentes demo e deixar base limpa para webhook conversacional.

## Features

- F00.1 Remover agentes demo do runtime.
- F00.2 Simplificar app para FastAPI base com `/health`.
- F00.3 Remover configs antigas sem uso.
- F00.4 Adicionar teste minimo de health.

## Resumo da fase

Base limpa e preparada para evolucao incremental por fases.

## Testes

- Automatizado: health endpoint.
- Manual: subida local da API e resposta 200 em `/health`.

---

## Fase 01 - setup de repositorio e qualidade

## Objetivo

Padronizar dependencias, ambiente e esteira minima de qualidade.

## Features

- F01.1 Dependencias pinadas no `pyproject.toml`.
- F01.2 `.env.example` padrao com variaveis obrigatorias.
- F01.3 Base de testes + CI (`ruff`, `mypy`, `pytest`).

## Resumo da fase

Projeto ganhou previsibilidade de ambiente e validacao continua no CI.

## Testes

- Automatizado: testes de dependencia, env example e health.
- Manual: bootstrap local com `.env` e validacao de comandos.

---

## Fase 02 - configuracao central e prompts

## Objetivo

Centralizar configuracoes e preparar composicao modular de prompt.

## Features

- F02.1 `Settings` centralizados com fail-fast.
- F02.2 `load_prompt()` com ordem de composicao definida.

## Resumo da fase

Configuracao e prompts ficaram padronizados, testaveis e reutilizaveis.

## Testes

- Automatizado: defaults, obrigatoriedade de variaveis e ordem de prompts.
- Manual: validacao de carregamento de prompt real.

---

## Fase 03 - banco e lead service

## Objetivo

Entregar camada de persistencia estavel para sessao/lead.

## Features

- F03.1 Estrategia de URL multi-provider (local/Supabase/Neon).
- F03.2 SQLAlchemy async + modelo `Lead`.
- F03.3 Alembic + migration inicial `leads`.
- F03.4 `LeadService` com `upsert` idempotente e `get_by_phone`.
- F03.5 Documentacao operacional da fase.

## Resumo da fase

Persistencia pronta, migration versionada e contrato de lead consolidado.

## Testes

- Automatizado: db url, sessao, modelo, alembic, migration contract, lead service.
- Manual: `upgrade/downgrade/upgrade`, validacao de tabela e idempotencia SQL.

---

## Fase 04 - integracoes HTTP (CRM + Sender) [PLANEJADA]

## Objetivo

Desacoplar integracoes externas para qualquer cliente (Helena como default de referencia).

## Features

- F04.1 HTTP client base resiliente (timeout, retry, erros, logs seguros).
- F04.2 `CRMClient` configuravel por env (rota/token/base_url).
- F04.3 Adapter default de CRM (Helena) mantendo contrato generico.
- F04.4 `WhatsAppSenderClient` configuravel por env.
- F04.5 Politica de erro/retry para 429/5xx e erros terminais.
- F04.6 Contratos de request/response documentados por adapter.

## Resumo esperado da fase

Integracoes sem hardcode, trocando CRM/Sender apenas por configuracao.

## Testes da fase 4

- Por feature (durante implementacao):
  - unitarios de parse, auth header, timeout, retry.
  - testes de contrato HTTP com mocks.
- Gate de fechamento da fase:
  - `uv run ruff check .`
  - `uv run mypy .`
  - `uv run pytest -q tests/test_http_client.py tests/test_crm_client.py tests/test_sender_client.py tests/test_retry_policy.py`
- Manual:
  - smoke com URLs de sandbox.
  - validacao de erro 401/404/429/500.

---

## Fase 05 - preprocessor multimodal [PLANEJADA]

## Objetivo

Normalizar e enriquecer entrada multimodal (texto, audio, imagem, pdf).

## Features

- F05.1 Normalizador de evento canonico de entrada.
- F05.2 Transcricao de audio com provider configuravel.
- F05.3 Analise de imagem (extracao textual/contextual).
- F05.4 Processamento de PDF (quando aplicavel).
- F05.5 Composer final de contexto para agente (prioridade e merge deterministico).
- F05.6 Fallback seguro para arquivos invalidos/falhas de provider.

## Resumo esperado da fase

Entrada multimodal fica previsivel e pronta para decisao do agente.

## Testes da fase 5

- Por feature (durante implementacao):
  - unitarios por tipo de midia.
  - fixtures reais de payload.
- Gate de fechamento da fase:
  - `uv run ruff check .`
  - `uv run mypy .`
  - `uv run pytest -q tests/test_event_normalizer.py tests/test_audio_preprocessor.py tests/test_image_preprocessor.py tests/test_pdf_preprocessor.py tests/test_message_composer.py`
- Manual:
  - envio de exemplos reais por texto/audio/imagem/pdf.

---

## Checkpoint obrigatorio apos fase 4 + fase 5

## Objetivo

Validar integracao conjunta antes de entrar na orquestracao do agente.

## Cenarios minimos

1. Texto -> CRM lookup -> resposta enviada.
2. Audio -> transcricao -> resposta enviada.
3. Imagem -> analise -> resposta enviada.
4. Erro temporario no CRM -> retry controlado.
5. Erro temporario no Sender -> retry controlado.
6. Evento duplicado -> sem resposta duplicada.

## Criterio de aprovacao

- Gate fase 4 verde.
- Gate fase 5 verde.
- Checkpoint integrado aprovado.

---

## Fase 06 - orquestracao do agente [PLANEJADA]

## Objetivo

Migrar regras de conversa para backend com prompt modular versionado.

## Features

- F06.1 `AgentFactory` com carregamento de prompts modulares.
- F06.2 Sessao single-client (`AGENT_SESSION_PREFIX + telefone`).
- F06.3 Regras de FAQ, qualificacao e transferencia por departamento.
- F06.4 Geracao de comments estruturados para handoff humano.
- F06.5 Guardrails de resposta (limites, tom, proibicoes).

## Testes

- Unitarios de roteamento/intencao.
- Contrato de transferencia (departmentId + comments).
- Simulacao de cenarios de objecao/FAQ/pedido de humano.

---

## Fase 07 - webhook completo e pipeline E2E [PLANEJADA]

## Objetivo

Fechar fluxo ponta a ponta no backend.

## Features

- F07.1 Endpoint `POST /webhook/whatsapp` com schema validado.
- F07.2 Pipeline: normalizar -> lead upsert -> CRM -> agente -> sender.
- F07.3 Idempotencia por `message_id`/`event_id`.
- F07.4 Tratamento de comando de sessao (ex.: reset).
- F07.5 Persistencia de metadados importantes (`crm_contact_id`, status).

## Testes

- Integracao completa do endpoint.
- E2E curto com mocks de CRM/Sender.
- Regressao de idempotencia.

---

## Fase 08 - qualidade operacional e seguranca [PLANEJADA]

## Objetivo

Aumentar confiabilidade para template de producao.

## Features

- F08.1 Logs estruturados com correlation id.
- F08.2 Padrao de erro observavel e auditavel.
- F08.3 Politica de segredos (sem token hardcoded em codigo/workflow).
- F08.4 Cobertura minima de testes definida.
- F08.5 Validacao de migration no CI.

## Testes

- Testes de observabilidade (campos obrigatorios de log).
- Pipeline CI completo.
- Checklist de seguranca aprovado.

---

## Fase 09 - template n8n oficial plugavel [PLANEJADA]

## Objetivo

Entregar fluxo n8n base desacoplado de cliente especifico.

## Features

- F09.1 Workflow n8n base com credenciais/env vars.
- F09.2 Remover hardcodes de URL/token/session key fixa.
- F09.3 Presets por cliente (Helena default).
- F09.4 Documento "onde customizar" (CRM, sender, departamentos, prompts).
- F09.5 Smoke test n8n -> API -> CRM/Sender.

## Testes

- Importacao do workflow em ambiente limpo.
- Validacao de credenciais obrigatorias.
- Teste funcional de uma conversa completa.

---

## Fase 10 - publicacao do template no GitHub [PLANEJADA]

## Objetivo

Finalizar pacote de template pronto para replicar por cliente.

## Features

- F10.1 Checklist de release.
- F10.2 Guia de onboarding por cliente.
- F10.3 Changelog e versionamento.
- F10.4 Pipeline de release.
- F10.5 Documentacao final de operacao.

## Testes

- Dry-run de onboarding em ambiente novo.
- Confirmacao de build/test/lint/migrations.
- Validacao manual final de fluxo completo.

---

## Estrategia oficial de testes (resumo)

- Teste continuo por feature (nao acumular para o final).
- Gate de fechamento em toda fase.
- Checkpoint integrado obrigatorio entre fases criticas (F4+F5).
- E2E antes de publicacao (F10).

## Ordem recomendada de execucao

1. Fase 04 + testes da fase 04.
2. Fase 05 + testes da fase 05.
3. Checkpoint integrado F4+F5.
4. Fase 06.
5. Fase 07.
6. Fase 08.
7. Fase 09.
8. Fase 10.

## Definicao de pronto (DoD) por feature

- Implementacao concluida.
- Testes automatizados minimos (feliz + falha principal).
- Documentacao da feature em `docs/features/`.
- Sem hardcode de segredo/URL.
- Gate da fase permanece verde.
