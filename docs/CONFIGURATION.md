# Referencia de Configuracao - Template Conversacional Agno

Este documento lista todas as variaveis de ambiente disponiveis no template, com descricao, valores possiveis e exemplos.

## Indice

- [Banco de Dados](#banco-de-dados)
- [Provider de Modelo de IA](#provider-de-modelo-de-ia)
- [CRM](#crm)
- [WhatsApp Sender](#whatsapp-sender)
- [Preprocessor Multimodal](#preprocessor-multimodal)
- [Agente](#agente)
- [Observabilidade](#observabilidade)
- [Seguranca](#seguranca)

---

## Banco de Dados

### `DATABASE_URL`

- **Descricao**: URL de conexao async com o banco PostgreSQL
- **Formato**: `postgresql+asyncpg://user:password@host:port/database`
- **Obrigatorio**: Sim
- **Default**: `postgresql+asyncpg://postgres:postgres@db:5432/agno_template`
- **Exemplo**:
  ```env
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agno_template
  ```

### `DATABASE_URL_MIGRATIONS`

- **Descricao**: URL de conexao sincrona para Alembic migrations
- **Formato**: `postgresql://user:password@host:port/database`
- **Obrigatorio**: Sim
- **Default**: `postgresql://postgres:postgres@db:5432/agno_template`
- **Exemplo**:
  ```env
  DATABASE_URL_MIGRATIONS=postgresql://postgres:postgres@localhost:5432/agno_template
  ```

### Providers suportados

- **Local**: PostgreSQL em Docker Compose
- **Supabase**: `postgresql+asyncpg://postgres:[password]@db.[project].supabase.co:5432/postgres`
- **Neon**: `postgresql+asyncpg://[user]:[password]@[host].neon.tech/[database]`
- **Render**: `postgresql+asyncpg://[user]:[password]@[host].render.com/[database]`

---

## Provider de Modelo de IA

### `AGENT_MODEL_PROVIDER`

- **Descricao**: Provider do modelo de IA para o agente
- **Valores possiveis**: `openai`, `openrouter`, `groq`, `claude`, `gemini`, `chatgpt`
- **Obrigatorio**: Sim
- **Default**: `openai`
- **Exemplo**:
  ```env
  AGENT_MODEL_PROVIDER=openai
  ```

### `AGENT_MODEL_ID`

- **Descricao**: ID do modelo especifico a ser usado
- **Obrigatorio**: Sim
- **Default**: `gpt-4o-mini`
- **Exemplos por provider**:
  - OpenAI: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`
  - OpenRouter: `anthropic/claude-3.5-sonnet`, `google/gemini-pro-1.5`
  - Groq: `llama-3.3-70b-versatile`, `mixtral-8x7b-32768`
  - Claude: `claude-3-5-sonnet-20241022`
  - Gemini: `gemini-1.5-pro`, `gemini-1.5-flash`

### `AGENT_MODEL_API_KEY`

- **Descricao**: API key do provider de modelo
- **Obrigatorio**: Sim (ou usar variavel especifica do provider)
- **Exemplo**:
  ```env
  AGENT_MODEL_API_KEY=sk-...
  ```

### `AGENT_MODEL_BASE_URL`

- **Descricao**: URL base customizada para o provider (opcional)
- **Obrigatorio**: Nao
- **Default**: URL padrao do provider
- **Exemplo**:
  ```env
  AGENT_MODEL_BASE_URL=https://api.openai.com/v1
  ```

### Variaveis especificas por provider

#### OpenAI

```env
OPENAI_API_KEY=sk-...
```

#### OpenRouter

```env
OPENROUTER_API_KEY=sk-or-v1-...
```

#### Groq

```env
GROQ_API_KEY=gsk_...
```

#### Anthropic (Claude)

```env
ANTHROPIC_API_KEY=sk-ant-...
```

---

## CRM

### `CRM_BASE_URL`

- **Descricao**: URL base da API do CRM
- **Obrigatorio**: Sim
- **Default**: `https://api.helena.app`
- **Exemplo**:
  ```env
  CRM_BASE_URL=https://api.helena.app
  ```

### `CRM_API_TOKEN`

- **Descricao**: Token de autenticacao da API do CRM
- **Obrigatorio**: Sim
- **Exemplo**:
  ```env
  CRM_API_TOKEN=seu-token-aqui
  ```

### `CRM_TIMEOUT`

- **Descricao**: Timeout em segundos para requisicoes ao CRM
- **Obrigatorio**: Nao
- **Default**: `30`
- **Exemplo**:
  ```env
  CRM_TIMEOUT=30
  ```

### `CRM_MAX_RETRIES`

- **Descricao**: Numero maximo de tentativas em caso de erro temporario
- **Obrigatorio**: Nao
- **Default**: `3`
- **Exemplo**:
  ```env
  CRM_MAX_RETRIES=3
  ```

---

## WhatsApp Sender

### `WHATSAPP_SENDER_BASE_URL`

- **Descricao**: URL base da API do sender de WhatsApp
- **Obrigatorio**: Sim
- **Exemplo**:
  ```env
  WHATSAPP_SENDER_BASE_URL=https://api.sender.com
  ```

### `WHATSAPP_SENDER_API_TOKEN`

- **Descricao**: Token de autenticacao da API do sender
- **Obrigatorio**: Sim
- **Exemplo**:
  ```env
  WHATSAPP_SENDER_API_TOKEN=seu-token-aqui
  ```

### `WHATSAPP_SENDER_TIMEOUT`

- **Descricao**: Timeout em segundos para requisicoes ao sender
- **Obrigatorio**: Nao
- **Default**: `30`
- **Exemplo**:
  ```env
  WHATSAPP_SENDER_TIMEOUT=30
  ```

### `WHATSAPP_SENDER_MAX_RETRIES`

- **Descricao**: Numero maximo de tentativas em caso de erro temporario
- **Obrigatorio**: Nao
- **Default**: `3`
- **Exemplo**:
  ```env
  WHATSAPP_SENDER_MAX_RETRIES=3
  ```

---

## Preprocessor Multimodal

### Audio (Transcricao)

#### `AUDIO_TRANSCRIPTION_PROVIDER`

- **Descricao**: Provider para transcricao de audio
- **Valores possiveis**: `openai`, `groq`, `assemblyai`
- **Obrigatorio**: Nao
- **Default**: `openai`
- **Exemplo**:
  ```env
  AUDIO_TRANSCRIPTION_PROVIDER=openai
  ```

#### `AUDIO_TRANSCRIPTION_MODEL`

- **Descricao**: Modelo especifico para transcricao
- **Obrigatorio**: Nao
- **Default**: `whisper-1` (OpenAI)
- **Exemplo**:
  ```env
  AUDIO_TRANSCRIPTION_MODEL=whisper-1
  ```

### Imagem (Analise)

#### `IMAGE_ANALYSIS_PROVIDER`

- **Descricao**: Provider para analise de imagem
- **Valores possiveis**: `openai`, `anthropic`, `google`
- **Obrigatorio**: Nao
- **Default**: `openai`
- **Exemplo**:
  ```env
  IMAGE_ANALYSIS_PROVIDER=openai
  ```

#### `IMAGE_ANALYSIS_MODEL`

- **Descricao**: Modelo especifico para analise de imagem
- **Obrigatorio**: Nao
- **Default**: `gpt-4o-mini` (OpenAI)
- **Exemplo**:
  ```env
  IMAGE_ANALYSIS_MODEL=gpt-4o-mini
  ```

### PDF (Processamento)

#### `PDF_PROCESSING_ENABLED`

- **Descricao**: Habilitar processamento de PDF
- **Valores possiveis**: `true`, `false`
- **Obrigatorio**: Nao
- **Default**: `true`
- **Exemplo**:
  ```env
  PDF_PROCESSING_ENABLED=true
  ```

---

## Agente

### `AGENT_SESSION_PREFIX`

- **Descricao**: Prefixo para identificacao de sessao do agente
- **Obrigatorio**: Nao
- **Default**: `agno_session`
- **Exemplo**:
  ```env
  AGENT_SESSION_PREFIX=cliente_session
  ```

### `AGENT_MAX_TOKENS`

- **Descricao**: Numero maximo de tokens na resposta do agente
- **Obrigatorio**: Nao
- **Default**: `1000`
- **Exemplo**:
  ```env
  AGENT_MAX_TOKENS=1000
  ```

### `AGENT_TEMPERATURE`

- **Descricao**: Temperatura do modelo (0.0 a 2.0)
- **Obrigatorio**: Nao
- **Default**: `0.7`
- **Exemplo**:
  ```env
  AGENT_TEMPERATURE=0.7
  ```

### `AGENT_TIMEOUT`

- **Descricao**: Timeout em segundos para requisicoes ao modelo
- **Obrigatorio**: Nao
- **Default**: `60`
- **Exemplo**:
  ```env
  AGENT_TIMEOUT=60
  ```

---

## Observabilidade

### `LOG_LEVEL`

- **Descricao**: Nivel de log da aplicacao
- **Valores possiveis**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Obrigatorio**: Nao
- **Default**: `INFO`
- **Exemplo**:
  ```env
  LOG_LEVEL=INFO
  ```

### `LOG_FORMAT`

- **Descricao**: Formato de log
- **Valores possiveis**: `json`, `text`
- **Obrigatorio**: Nao
- **Default**: `json`
- **Exemplo**:
  ```env
  LOG_FORMAT=json
  ```

### `CORRELATION_ID_HEADER`

- **Descricao**: Nome do header HTTP para correlation ID
- **Obrigatorio**: Nao
- **Default**: `X-Correlation-Id`
- **Exemplo**:
  ```env
  CORRELATION_ID_HEADER=X-Correlation-Id
  ```

---

## Seguranca

### `API_SECRET_KEY`

- **Descricao**: Chave secreta para assinatura de tokens (se aplicavel)
- **Obrigatorio**: Nao (depende da feature)
- **Exemplo**:
  ```env
  API_SECRET_KEY=sua-chave-secreta-aqui
  ```

### `ALLOWED_ORIGINS`

- **Descricao**: Origens permitidas para CORS (separadas por virgula)
- **Obrigatorio**: Nao
- **Default**: `*`
- **Exemplo**:
  ```env
  ALLOWED_ORIGINS=https://app.cliente.com,https://admin.cliente.com
  ```

---

## Exemplo completo de .env

```env
# Banco de dados
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/agno_template
DATABASE_URL_MIGRATIONS=postgresql://postgres:postgres@db:5432/agno_template

# Provider de modelo
AGENT_MODEL_PROVIDER=openai
AGENT_MODEL_ID=gpt-4o-mini
AGENT_MODEL_API_KEY=sk-...

# CRM
CRM_BASE_URL=https://api.helena.app
CRM_API_TOKEN=seu-token-helena
CRM_TIMEOUT=30

# WhatsApp Sender
WHATSAPP_SENDER_BASE_URL=https://api.sender.com
WHATSAPP_SENDER_API_TOKEN=seu-token-sender
WHATSAPP_SENDER_TIMEOUT=30

# Preprocessor multimodal
OPENAI_API_KEY=sk-...
AUDIO_TRANSCRIPTION_PROVIDER=openai
IMAGE_ANALYSIS_PROVIDER=openai

# Agente
AGENT_SESSION_PREFIX=agno_session
AGENT_MAX_TOKENS=1000
AGENT_TEMPERATURE=0.7

# Observabilidade
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Validacao de configuracao

Para validar sua configuracao, execute:

```bash
python scripts/validate_config.py
```

Ou use o checklist de release:

```bash
python scripts/pre_release_check.py
```

---

## Proximos passos

- [Voltar ao Onboarding](./ONBOARDING.md)
- [Customizar o template](./CUSTOMIZATION.md)
- [Ver exemplos de configuracao](./examples/)
