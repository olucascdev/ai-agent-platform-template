# Fase 7 - webhook completo e pipeline E2E

## Status

- Concluida.

## Features concluidas

### Feature 7.1 - endpoint `POST /webhook/whatsapp` com schema validado

- Endpoint de webhook criado com contrato de entrada validado por schema.
- Suporte adicionado para payload direto e payload com wrapper `body`.
- Validacoes de sessao e telefone aplicadas no schema para rejeicao fail-fast.
- Resposta `202 Accepted` padronizada para confirmar aceite inicial do evento.
- Cobertura automatizada adicionada para cenarios de aceite e rejeicao do contrato.

### Feature 7.2 - pipeline: normalizar -> lead upsert -> CRM -> agente -> sender

- Service E2E de webhook implementado para executar o pipeline completo do backend em sequencia.
- Integracao de normalizacao, lead upsert, CRM lookup, preprocessamento, agente, guardrails e sender consolidada em unico fluxo.
- Endpoint de webhook atualizado para usar o pipeline com dependencia injetada e manter contrato HTTP da fase 7.1.
- Resultado interno do pipeline estruturado com metadados de lead/CRM/envio para futuras etapas da fase 7.
- Cobertura automatizada adicionada para ordem de execucao e fallback de guardrails antes do envio.

### Feature 7.3 - idempotencia por `message_id`/`event_id`

- Servico de idempotencia implementado para registrar eventos processados por identificadores estaveis.
- Tabela dedicada de idempotencia adicionada com constraints para evitar reprocessamento de eventos repetidos.
- Pipeline atualizado para interromper efeitos colaterais quando evento e identificado como duplicado.
- Endpoint atualizado com retorno `is_duplicate` para visibilidade operacional da decisao idempotente.
- Cobertura automatizada adicionada para servico, pipeline, endpoint e contrato de migration.

### Feature 7.4 - tratamento de comando de sessao (ex.: reset)

- Tratamento de comando de sessao adicionado ao pipeline de webhook com suporte ao comando `reset`.
- Fluxo de comando implementado com short-circuit para evitar CRM/preprocessamento/LLM quando reset e solicitado.
- Reset de sessao do agente executado em modo best-effort e confirmacao enviada ao usuario pelo sender.
- Resposta HTTP e resultado interno do pipeline expostos com campo `session_command` para observabilidade.
- Cobertura automatizada adicionada para resolucao de comando, pipeline e endpoint.

### Feature 7.5 - persistencia de metadados importantes (`crm_contact_id`, status)

- Persistencia de metadados operacionais implementada no `LeadService` para gravar `crm_contact_id` e `status`.
- Coluna `status` adicionada no modelo `Lead` e migration aplicada para evolucao de schema.
- Pipeline atualizado para registrar status por fluxo (`message_sent`, `session_reset`, `duplicate_ignored`).
- Resultado interno do pipeline ampliado com `lead_status` para rastreabilidade das execucoes.
- Cobertura automatizada adicionada para service, pipeline, modelo e contrato de migration.

## Proximas features da fase

- Nenhuma. Fase 7 finalizada.
