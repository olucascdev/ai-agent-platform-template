# 🚀 Guia Completo de Implementação - Agno Conversational Template

**Tempo estimado: 30-45 minutos**

Este guia consolida TODAS as informações necessárias para implementar o template Agno para um novo cliente, do zero até a produção.

---

## 📋 Índice

1. [Visão Geral do Template](#1-visão-geral-do-template)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Checklist de Informações do Cliente](#3-checklist-de-informações-do-cliente)
4. [Setup Inicial](#4-setup-inicial)
5. [Configuração do Banco de Dados](#5-configuração-do-banco-de-dados)
6. [Configuração das Integrações](#6-configuração-das-integrações)
7. [Configuração do Agente IA](#7-configuração-do-agente-ia)
8. [Criação das Tabelas](#8-criação-das-tabelas)
9. [Teste do Fluxo Completo](#9-teste-do-fluxo-completo)
10. [Customização por Cliente](#10-customização-por-cliente)
11. [Deploy em Produção](#11-deploy-em-produção)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Visão Geral do Template

### O que o template faz?

O Agno é um template de agente conversacional que:

✅ **Recebe mensagens** do WhatsApp via webhook  
✅ **Verifica/cria leads** no banco de dados  
✅ **Busca contatos** no CRM (opcional)  
✅ **Processa mídia** (áudio, imagem, PDF)  
✅ **Envia para IA** (OpenAI, Groq, Claude, etc)  
✅ **Responde via WhatsApp** automaticamente  
✅ **Mantém contexto** da conversa por cliente  
✅ **Evita duplicatas** (idempotência)  

### Fluxo do Pipeline

```
WhatsApp → Webhook → Verifica Lead → Busca CRM → Processa Mídia → IA → Responde
```

### Arquitetura

- **Backend**: FastAPI (Python 3.12+)
- **Banco**: PostgreSQL (Supabase, Neon, local)
- **IA**: Multi-provider (OpenAI, Groq, Claude, Gemini)
- **Integrações**: CRM + WhatsApp Sender (configuráveis)

---

## 2. Pré-requisitos

### Ferramentas Necessárias

- [ ] **Docker** e **Docker Compose** instalados
- [ ] **Git** instalado
- [ ] **Python 3.12+** (para desenvolvimento local)
- [ ] **uv** (gerenciador Python) - [Instalar](https://docs.astral.sh/uv/getting-started/installation/)
- [ ] Editor de código (VS Code recomendado)

### Verificar instalação

```bash
docker --version          # Docker version 20.10+
docker compose version    # Docker Compose version 2.0+
python --version          # Python 3.12+
git --version            # Git version 2.0+
```

---

## 3. Checklist de Informações do Cliente

Antes de começar, colete estas informações do cliente:

### 🔴 Obrigatórias

- [ ] **Nome do agente**: Ex: "Helena", "Luna", "Maria"
- [ ] **Prefixo de sessão**: Ex: "spacecont", "cliente_a" (sem espaços)
- [ ] **Banco de dados**: URL do Supabase/Neon ou criar novo
- [ ] **API Key da IA**: OpenAI, Groq, Claude ou outro
- [ ] **CRM**: URL base + Token Bearer
- [ ] **WhatsApp Sender**: URL + Token Bearer

### 🟡 Opcionais (mas recomendadas)

- [ ] **Google API Key**: Para análise de imagem (Gemini)
- [ ] **Timezone**: Ex: "America/Sao_Paulo"
- [ ] **Customer Tier**: Ex: "diamante", "gold", "silver"
- [ ] **Prompts customizados**: Regras de conversa específicas
- [ ] **FAQ**: Perguntas frequentes do negócio
- [ ] **Departamentos**: IDs dos departamentos no CRM

---

## 4. Setup Inicial

### 4.1. Clonar o repositório

```bash
# Clone o projeto
git clone <url-do-repositorio>
cd agno-conversational-template

# Verificar estrutura
ls -la
```

### 4.2. Copiar arquivo de configuração

```bash
# Copiar template de configuração
cp .env.example .env

# Abrir para edição
nano .env  # ou code .env (VS Code)
```

---

## 5. Configuração do Banco de Dados

### Opção A: Supabase (Recomendado para produção)

#### 5.1. Criar projeto no Supabase

1. Acesse: https://app.supabase.com
2. Clique em "New Project"
3. Preencha:
   - **Name**: `agno-cliente-nome`
   - **Database Password**: Gere uma senha forte
   - **Region**: Escolha mais próxima do cliente
4. Aguarde criação (~2 minutos)

#### 5.2. Obter URL de conexão

1. No projeto, vá em **Settings** → **Database**
2. Role até **Connection string** → **URI**
3. Copie a URL (formato: `postgresql://postgres:[PASSWORD]@...`)
4. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha do projeto

#### 5.3. Configurar no .env

```env
# Supabase - Conexão async (runtime)
DATABASE_URL=postgresql+asyncpg://postgres:SUA_SENHA@db.abc123xyz.supabase.co:5432/postgres

# Supabase - Conexão para migrations (opcional, mas recomendado)
DATABASE_URL_MIGRATIONS=postgresql+asyncpg://postgres:SUA_SENHA@db.abc123xyz.supabase.co:5432/postgres
```

**Dica**: Se usar Supabase Pooler (recomendado para serverless):
```env
DATABASE_URL=postgresql+asyncpg://postgres:SENHA@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

### Opção B: Neon (Alternativa serverless)

#### 5.1. Criar projeto no Neon

1. Acesse: https://neon.tech
2. Clique em "Create Project"
3. Copie a connection string fornecida

#### 5.2. Configurar no .env

```env
DATABASE_URL=postgresql+asyncpg://user:senha@ep-cool-name-123456.us-east-2.aws.neon.tech:5432/neondb
```

### Opção C: PostgreSQL Local (Desenvolvimento)

```env
# Docker Compose já configura automaticamente
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/agno_template
DATABASE_URL_MIGRATIONS=postgresql://postgres:postgres@db:5432/agno_template
```

---

## 6. Configuração das Integrações

### 6.1. CRM (Helena ou outro)

#### Onde obter as informações:

**Helena CRM:**
1. Acesse o painel Helena
2. Vá em **Configurações** → **Integrações** → **API**
3. Copie:
   - **URL Base**: `https://api.helena.app` (ou URL do cliente)
   - **Token**: Gere um novo token de API

**Outro CRM:**
1. Consulte documentação do CRM
2. Obtenha URL base da API
3. Gere token de autenticação

#### Configurar no .env:

```env
# CRM - Configuração básica
CRM_BASE_URL=https://api.helena.app
CRM_TOKEN=seu-token-bearer-aqui

# CRM - Configurações avançadas (opcional)
CRM_CONTACTS_LOOKUP_PATH=/contacts
CRM_LOOKUP_PHONE_PARAM=phone
CRM_LOOKUP_PHONE_VALUE_TEMPLATE={phone}
CRM_AUTH_HEADER_NAME=Authorization
CRM_AUTH_HEADER_PREFIX=Bearer
```

#### Configurar no .env:

```env
# WhatsApp Sender - Configuração básica
WHATSAPP_SENDER_URL=https://api.wts.chat/chat/v1/session/{session_id}/message
WHATSAPP_TOKEN=seu-token-bearer-aqui

# WhatsApp Sender - Configurações avançadas (opcional)
WHATSAPP_SENDER_METHOD=POST
WHATSAPP_SENDER_INCLUDE_NUMBER=true
WHATSAPP_SENDER_NUMBER_FIELD=number
WHATSAPP_SENDER_TEXT_FIELD=text
WHATSAPP_SENDER_AUTH_HEADER_NAME=Authorization
WHATSAPP_SENDER_AUTH_HEADER_PREFIX=Bearer
```

---

## 7. Configuração do Agente IA

### 7.1. Escolher Provider

Escolha um provider de IA baseado nas necessidades:

| Provider | Vantagens | Desvantagens | Custo |
|----------|-----------|--------------|-------|
| **OpenAI** | Melhor qualidade, confiável | Mais caro | $$$ |
| **Groq** | Muito rápido, gratuito | Limite de requisições | Grátis/$ |
| **Claude** | Ótimo para conversas longas | Requer API key paga | $$$ |
| **Gemini** | Bom custo-benefício | Qualidade média | $$ |
| **OpenRouter** | Acesso a vários modelos | Complexidade extra | $$ |

### 7.2. Configurar Provider Escolhido

#### Opção A: OpenAI (Recomendado)

**Obter API Key:**
1. Acesse: https://platform.openai.com
2. Vá em **API Keys**
3. Clique em **Create new secret key**
4. Copie a chave (começa com `sk-`)

**Configurar:**
```env
AGENT_MODEL_PROVIDER=openai
AGENT_MODEL_ID=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Para análise de imagem e transcrição de áudio
GOOGLE_API_KEY=sua-chave-google  # Opcional
```

#### Opção B: Groq (Rápido e gratuito)

**Obter API Key:**
1. Acesse: https://console.groq.com
2. Vá em **API Keys**
3. Crie nova chave
4. Copie a chave (começa com `gsk_`)

**Configurar:**
```env
AGENT_MODEL_PROVIDER=groq
AGENT_MODEL_ID=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
```

#### Opção C: Claude (Anthropic)

**Obter API Key:**
1. Acesse: https://console.anthropic.com
2. Vá em **API Keys**
3. Crie nova chave
4. Copie a chave (começa com `sk-ant-`)

**Configurar:**
```env
AGENT_MODEL_PROVIDER=claude
AGENT_MODEL_ID=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

#### Opção D: OpenRouter (Multi-modelo)

**Obter API Key:**
1. Acesse: https://openrouter.ai
2. Faça login
3. Vá em **Keys**
4. Crie nova chave

**Configurar:**
```env
AGENT_MODEL_PROVIDER=openrouter
AGENT_MODEL_ID=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=sk-or-v1-...
```

### 7.3. Configurar Nome e Sessão do Agente

```env
# Nome do agente (aparece nas conversas)
AGENT_NAME=Helena

# Prefixo de sessão (identificador único do cliente)
AGENT_SESSION_PREFIX=spacecont

# Timezone do cliente
AGENT_TIMEZONE=America/Sao_Paulo

# Tier do cliente (opcional)
AGENT_CUSTOMER_TIER=diamante
```

---

## 8. Criação das Tabelas

O template precisa de 2 tabelas no banco:
- `leads`: Armazena contatos e sessões
- `processed_webhook_events`: Controla idempotência

### Opção A: Migrations Automáticas (Recomendado)

#### 8.1. Subir aplicação

```bash
docker compose up -d --build
```

#### 8.2. Executar migrations

```bash
# Via Docker
docker compose exec api alembic upgrade head

# Ou localmente (se tiver Python instalado)
alembic upgrade head
```

#### 8.3. Verificar tabelas criadas

**No Supabase:**
1. Vá em **Table Editor**
2. Deve ver: `leads`, `processed_webhook_events`, `alembic_version`

**No Neon:**
1. Vá em **Tables**
2. Deve ver as mesmas tabelas

### Opção B: SQL Manual (Alternativa)

Se preferir criar manualmente no SQL Editor:

```sql
-- Tabela de leads
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(32) UNIQUE NOT NULL,
    session_id VARCHAR(120) NOT NULL,
    agent_session_id VARCHAR(120) NOT NULL,
    crm_contact_id VARCHAR(120),
    status VARCHAR(40),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_leads_session_id ON leads(session_id);

-- Tabela de eventos processados (idempotência)
CREATE TABLE processed_webhook_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(191),
    message_id VARCHAR(191),
    session_id VARCHAR(120) NOT NULL,
    contact_phone VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    CONSTRAINT ck_processed_webhook_events_has_identifier 
        CHECK (event_id IS NOT NULL OR message_id IS NOT NULL)
);

CREATE UNIQUE INDEX uq_processed_webhook_events_event_id 
    ON processed_webhook_events(event_id);
CREATE UNIQUE INDEX uq_processed_webhook_events_message_id 
    ON processed_webhook_events(message_id);

-- Tabela de controle de migrations
CREATE TABLE alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);

INSERT INTO alembic_version VALUES ('20260422_0004');
```

---

## 9. Teste do Fluxo Completo

### 9.1. Verificar saúde da API

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

### 9.2. Acessar documentação interativa

Abra no navegador: http://localhost:8000/docs

### 9.3. Enviar mensagem de teste

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "test-001",
    "lastMessage": {
      "id": "msg-001",
      "fromMe": false,
      "type": "text",
      "body": "Olá, gostaria de informações sobre os serviços"
    },
    "contact": {
      "phone": "5511999999999",
      "name": "Cliente Teste"
    },
    "sessionId": "session-test-123",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

### 9.4. Verificar logs

```bash
# Ver logs em tempo real
docker compose logs -f api

# Ver últimas 100 linhas
docker compose logs --tail=100 api
```

**O que você deve ver nos logs:**
```
✅ webhook_whatsapp_received
✅ lead_upserted (criou/atualizou lead)
✅ crm_lookup_attempted (tentou buscar no CRM)
✅ agent_response_generated (IA respondeu)
✅ message_sent (enviou resposta)
✅ webhook_whatsapp_accepted
```

### 9.5. Verificar no banco de dados

**No Supabase/Neon:**
```sql
-- Ver lead criado
SELECT * FROM leads WHERE phone = '5511999999999';

-- Ver evento processado
SELECT * FROM processed_webhook_events WHERE event_id = 'test-001';
```

---

## 10. Customização por Cliente

### 10.1. Criar Prompts Customizados

```bash
# Criar diretório de prompts
mkdir -p prompts

# Criar prompt base
cat > prompts/identity.md << 'EOF'
# Identidade do Agente

Você é **Helena**, assistente virtual da **SpaceCont Contabilidade**.

## Seu Objetivo
Ajudar clientes com informações sobre serviços contábeis, tirar dúvidas e agendar consultorias.

## Tom de Voz
- Profissional mas acessível
- Claro e objetivo
- Empático e prestativo

## Regras
1. Sempre cumprimente o cliente pelo nome (se disponível)
2. Identifique a necessidade: informação, orçamento ou suporte
3. Seja breve (máximo 3 parágrafos por resposta)
4. Use emojis com moderação (apenas 1-2 por mensagem)
5. Sempre pergunte se pode ajudar em mais alguma coisa
EOF
```

### 10.2. Criar FAQ

```bash
cat > prompts/faq.md << 'EOF'
# Perguntas Frequentes

## Horário de Funcionamento
**P:** Qual o horário de atendimento?
**R:** Atendemos de segunda a sexta, das 9h às 18h.

## Serviços
**P:** Quais serviços vocês oferecem?
**R:** Oferecemos:
- Contabilidade completa para empresas
- Abertura de CNPJ
- Declaração de Imposto de Renda
- Consultoria tributária

## Preços
**P:** Quanto custa?
**R:** Os valores variam conforme o porte da empresa e serviços necessários. Posso agendar uma consultoria gratuita para fazer um orçamento personalizado?

## Contato
**P:** Como posso falar com um contador?
**R:** Posso transferir você para nossa equipe agora mesmo! Eles vão te atender em alguns minutos.
EOF
```

### 10.3. Configurar Departamentos

```bash
cat > prompts/departments.md << 'EOF'
# Departamentos para Transferência

## Vendas
- **ID**: dept_vendas_001
- **Quando transferir**: Cliente quer orçamento, contratar serviço
- **Palavras-chave**: "quero contratar", "quanto custa", "orçamento"

## Suporte
- **ID**: dept_suporte_001
- **Quando transferir**: Problema técnico, dúvida sobre processo
- **Palavras-chave**: "não consigo", "erro", "problema"

## Financeiro
- **ID**: dept_financeiro_001
- **Quando transferir**: Questões de pagamento, boleto, fatura
- **Palavras-chave**: "pagamento", "boleto", "fatura", "cobrança"
EOF
```

### 10.4. Configurar Carregamento de Prompts

Edite `app/config.py` se necessário, ou use a configuração padrão que já carrega os arquivos de `prompts/`.

---

## 11. Deploy em Produção

### 11.1. Preparar ambiente de produção

```bash
# Criar .env de produção
cp .env .env.production

# Editar com valores de produção
nano .env.production
```

**Diferenças importantes para produção:**
```env
# Usar banco de produção (Supabase/Neon)
DATABASE_URL=postgresql+asyncpg://...produção...

# Usar API keys de produção
OPENAI_API_KEY=sk-prod-...
CRM_TOKEN=token-producao-...
WHATSAPP_TOKEN=token-producao-...

# Configurar logs
LOG_LEVEL=INFO
LOG_FORMAT=json

# Segurança
ALLOWED_ORIGINS=https://app.cliente.com,https://admin.cliente.com
```

### 11.2. Deploy com Docker

```bash
# Build da imagem
docker build -t agno-cliente-nome:latest .

# Rodar em produção
docker run -d \
  --name agno-cliente-nome \
  --env-file .env.production \
  -p 8000:8000 \
  agno-cliente-nome:latest
```

### 11.3. Deploy em Cloud (Render, Railway, Fly.io)

**Render:**
1. Conecte repositório GitHub
2. Configure variáveis de ambiente
3. Deploy automático

**Railway:**
1. Conecte repositório
2. Configure variáveis
3. Deploy automático

**Fly.io:**
```bash
fly launch
fly secrets set DATABASE_URL="..." OPENAI_API_KEY="..."
fly deploy
```

### 11.4. Configurar Webhook no WhatsApp

Configure o webhook do WhatsApp para apontar para:
```
https://seu-dominio.com/webhook/whatsapp
```

---

## 12. Troubleshooting

### Problema: API não sobe

**Sintomas:**
- `docker compose up` falha
- API não responde em http://localhost:8000

**Soluções:**
```bash
# 1. Verificar logs
docker compose logs api

# 2. Verificar se portas estão livres
lsof -i :8000
lsof -i :5432

# 3. Recriar containers
docker compose down
docker compose up --build

# 4. Verificar .env
cat .env | grep -v "^#" | grep -v "^$"
```

### Problema: Migrations falham

**Sintomas:**
- `alembic upgrade head` retorna erro
- Tabelas não são criadas

**Soluções:**
```bash
# 1. Verificar conexão com banco
docker compose exec api python -c "from db.session import async_engine; import asyncio; asyncio.run(async_engine.connect())"

# 2. Verificar URL do banco
echo $DATABASE_URL

# 3. Resetar banco (CUIDADO: apaga dados)
docker compose down -v
docker compose up -d
alembic upgrade head

# 4. Criar tabelas manualmente (ver seção 8.2)
```

### Problema: Webhook retorna erro 500

**Sintomas:**
- POST /webhook/whatsapp retorna 500
- Logs mostram erro interno

**Soluções:**
```bash
# 1. Ver logs detalhados
docker compose logs -f api

# 2. Verificar variáveis obrigatórias
env | grep -E "(DATABASE_URL|OPENAI_API_KEY|CRM_|WHATSAPP_)"

# 3. Testar CRM isoladamente
curl -H "Authorization: Bearer $CRM_TOKEN" $CRM_BASE_URL/contacts

# 4. Testar provider de IA
docker compose exec api python -c "from app.agent.factory import build_agent_factory; factory = build_agent_factory(); agent = factory.build_for_phone(contact_phone='test', user_id='1'); print(agent)"
```

### Problema: Agente não responde

**Sintomas:**
- Webhook aceita mensagem (202)
- Mas não envia resposta no WhatsApp

**Soluções:**
```bash
# 1. Verificar API key da IA
echo $OPENAI_API_KEY

# 2. Verificar token do sender
echo $WHATSAPP_TOKEN

# 3. Ver logs do pipeline
docker compose logs api | grep -E "(agent_response|sender)"

# 4. Testar sender isoladamente
curl -X POST $WHATSAPP_SENDER_URL \
  -H "Authorization: Bearer $WHATSAPP_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"number":"5511999999999","text":"Teste"}'
```

### Problema: Duplicatas não são detectadas

**Sintomas:**
- Mesma mensagem processada múltiplas vezes
- Tabela `processed_webhook_events` vazia

**Soluções:**
```bash
# 1. Verificar se tabela existe
docker compose exec api python -c "from db.models import ProcessedWebhookEvent; print(ProcessedWebhookEvent.__tablename__)"

# 2. Verificar se webhook envia event_id ou message_id
# Ver logs: docker compose logs api | grep "eventId\|messageId"

# 3. Verificar índices únicos
# No Supabase: SELECT * FROM pg_indexes WHERE tablename = 'processed_webhook_events';
```

### Problema: Transcrição de áudio falha

**Sintomas:**
- Mensagens de áudio não são processadas
- Erro ao baixar/transcrever áudio

**Soluções:**
```bash
# 1. Verificar OPENAI_API_KEY
echo $OPENAI_API_KEY

# 2. Verificar URL do áudio
# Ver logs: docker compose logs api | grep "audio"

# 3. Testar Whisper isoladamente
docker compose exec api python -c "from app.preprocessing.audio_transcription import transcribe_audio; import asyncio; print(asyncio.run(transcribe_audio('URL_DO_AUDIO')))"
```

### Problema: Análise de imagem falha

**Sintomas:**
- Imagens não são analisadas
- Erro ao processar imagem

**Soluções:**
```bash
# 1. Verificar GOOGLE_API_KEY
echo $GOOGLE_API_KEY

# 2. Verificar provider de imagem
echo $IMAGE_ANALYSIS_PROVIDER

# 3. Testar análise isoladamente
docker compose exec api python -c "from app.preprocessing.image_analysis import analyze_image; import asyncio; print(asyncio.run(analyze_image('URL_DA_IMAGEM')))"
```

---

## 📚 Recursos Adicionais

### Documentação Complementar

- [ONBOARDING.md](./ONBOARDING.md) - Guia rápido de onboarding
- [CONFIGURATION.md](./CONFIGURATION.md) - Referência completa de variáveis
- [CUSTOMIZATION.md](./CUSTOMIZATION.md) - Guia de customização avançada
- [docs/examples/](./examples/) - Exemplos de configuração prontos

### Exemplos de .env Prontos

```bash
# Ver exemplos disponíveis
ls docs/examples/

# Copiar exemplo específico
cp docs/examples/helena-openai.env.example .env
```

### Scripts Úteis

```bash
# Validar configuração
python scripts/validate_config.py

# Checklist de release
python scripts/pre_release_check.py

# Bump de versão
python scripts/bump_version.py patch
```

---

## ✅ Checklist Final

Antes de considerar a implementação completa:

### Configuração
- [ ] .env configurado com todas variáveis obrigatórias
- [ ] Banco de dados criado e acessível
- [ ] Tabelas criadas (via migrations ou SQL manual)
- [ ] CRM configurado e testado
- [ ] WhatsApp Sender configurado e testado
- [ ] Provider de IA configurado e testado

### Testes
- [ ] API responde em /health
- [ ] Webhook aceita mensagem de teste
- [ ] Lead é criado no banco
- [ ] CRM é consultado (se configurado)
- [ ] Agente responde corretamente
- [ ] Mensagem é enviada via WhatsApp
- [ ] Idempotência funciona (duplicatas ignoradas)

### Customização
- [ ] Prompts customizados criados
- [ ] FAQ configurado
- [ ] Departamentos definidos
- [ ] Tom de voz ajustado
- [ ] Regras de transferência configuradas

### Produção
- [ ] .env.production configurado
- [ ] Deploy realizado
- [ ] Webhook configurado no WhatsApp
- [ ] Monitoramento configurado
- [ ] Logs funcionando

---

## 🎯 Próximos Passos

Após implementação completa:

1. **Monitorar primeiras conversas** - Ajustar prompts conforme necessário
2. **Coletar feedback** - Melhorar respostas do agente
3. **Otimizar custos** - Ajustar provider/modelo se necessário
4. **Escalar** - Adicionar mais clientes seguindo este guia

---

## 💬 Suporte

Para dúvidas ou problemas:

1. Consulte a seção [Troubleshooting](#12-troubleshooting)
2. Verifique logs: `docker compose logs -f api`
3. Consulte documentação complementar em `docs/`
4. Entre em contato com a equipe de desenvolvimento

---

**Tempo total estimado: 30-45 minutos**

**Última atualização: 22-04-2026**
