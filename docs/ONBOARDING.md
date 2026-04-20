# Guia de Onboarding - Template Conversacional Agno

Bem-vindo ao template conversacional Agno! Este guia vai te ajudar a configurar e personalizar o template para o seu cliente em menos de 30 minutos.

## Pre-requisitos

Antes de comecar, certifique-se de ter instalado:

- **Docker** e **Docker Compose** (para executar a aplicacao)
- **Python 3.12+** (para desenvolvimento local)
- **uv** (gerenciador de pacotes Python) - [Instalacao](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** (para clonar o repositorio)

## Passo 1: Clone do repositorio

```bash
git clone <url-do-repositorio>
cd agno-conversational-template
```

## Passo 2: Configuracao de variaveis de ambiente

### 2.1. Copiar arquivo de exemplo

```bash
cp .env.example .env
```

### 2.2. Configurar variaveis obrigatorias

Abra o arquivo `.env` e configure as seguintes variaveis:

#### Banco de dados

```env
# Para desenvolvimento local (Docker Compose ja configura automaticamente)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/agno_template
DATABASE_URL_MIGRATIONS=postgresql://postgres:postgres@db:5432/agno_template
```

#### Provider de modelo de IA

Escolha um provider e configure:

**Opcao 1: OpenAI (recomendado para producao)**
```env
AGENT_MODEL_PROVIDER=openai
AGENT_MODEL_ID=gpt-4o-mini
AGENT_MODEL_API_KEY=sk-...
```

**Opcao 2: OpenRouter (multiplos modelos)**
```env
AGENT_MODEL_PROVIDER=openrouter
AGENT_MODEL_ID=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=sk-or-v1-...
```

**Opcao 3: Groq (rapido e gratuito para testes)**
```env
AGENT_MODEL_PROVIDER=groq
AGENT_MODEL_ID=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
```

#### CRM (Helena como default)

```env
CRM_BASE_URL=https://api.helena.app
CRM_API_TOKEN=seu-token-helena
CRM_TIMEOUT=30
```

#### WhatsApp Sender

```env
WHATSAPP_SENDER_BASE_URL=https://api.sender.com
WHATSAPP_SENDER_API_TOKEN=seu-token-sender
WHATSAPP_SENDER_TIMEOUT=30
```

#### Preprocessor multimodal (opcional)

Para transcricao de audio e analise de imagem:

```env
OPENAI_API_KEY=sk-...  # Para Whisper (audio) e GPT-4 Vision (imagem)
```

### 2.3. Variaveis opcionais

Veja todas as variaveis disponiveis em [CONFIGURATION.md](./CONFIGURATION.md).

## Passo 3: Inicializacao do banco de dados

### 3.1. Subir servicos com Docker Compose

```bash
docker compose up -d
```

Isso vai:
- Subir o banco PostgreSQL
- Subir a API FastAPI
- Executar migrations automaticamente

### 3.2. Verificar saude da API

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "healthy"}
```

### 3.3. Acessar documentacao da API

Abra no navegador: http://localhost:8000/docs

## Passo 4: Primeira conversa de teste

### 4.1. Enviar mensagem de teste

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-001",
    "message_id": "msg-001",
    "phone": "+5511999999999",
    "message": "Ola, gostaria de informacoes",
    "timestamp": "2024-01-01T12:00:00Z"
  }'
```

### 4.2. Verificar logs

```bash
docker compose logs -f api
```

Voce deve ver:
- Normalizacao do evento
- Upsert do lead no banco
- Consulta ao CRM
- Processamento do agente
- Envio da resposta pelo Sender

## Passo 5: Customizacao (opcional)

Para customizar o template para o seu cliente, veja:

- **Prompts e regras de conversa**: [CUSTOMIZATION.md](./CUSTOMIZATION.md#prompts)
- **Departamentos e transferencias**: [CUSTOMIZATION.md](./CUSTOMIZATION.md#departamentos)
- **FAQ e qualificacao**: [CUSTOMIZATION.md](./CUSTOMIZATION.md#faq)
- **Trocar CRM/Sender**: [CUSTOMIZATION.md](./CUSTOMIZATION.md#integracoes)

## Passo 6: Desenvolvimento local (opcional)

Se voce quer desenvolver localmente sem Docker:

### 6.1. Instalar dependencias

```bash
uv sync
```

### 6.2. Ativar ambiente virtual

```bash
source .venv/bin/activate
```

### 6.3. Executar migrations

```bash
alembic upgrade head
```

### 6.4. Executar API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6.5. Executar testes

```bash
pytest
```

## Troubleshooting

### Problema: API nao sobe

**Sintoma**: `docker compose up` falha ou API nao responde

**Solucoes**:
1. Verificar se as portas 8000 e 5432 estao disponiveis
2. Verificar logs: `docker compose logs api`
3. Verificar se o banco esta rodando: `docker compose ps`
4. Recriar containers: `docker compose down && docker compose up --build`

### Problema: Migrations falham

**Sintoma**: Erro ao executar `alembic upgrade head`

**Solucoes**:
1. Verificar se `DATABASE_URL_MIGRATIONS` esta correto no `.env`
2. Verificar se o banco esta acessivel
3. Resetar banco (CUIDADO: apaga dados): `docker compose down -v && docker compose up -d`

### Problema: Webhook retorna erro 500

**Sintoma**: `POST /webhook/whatsapp` retorna erro interno

**Solucoes**:
1. Verificar logs da API: `docker compose logs -f api`
2. Verificar se todas variaveis obrigatorias estao configuradas
3. Verificar se CRM/Sender estao acessiveis
4. Verificar se o provider de modelo esta configurado corretamente

### Problema: Agente nao responde

**Sintoma**: Webhook aceita mensagem mas nao envia resposta

**Solucoes**:
1. Verificar se `AGENT_MODEL_API_KEY` esta correto
2. Verificar se `WHATSAPP_SENDER_API_TOKEN` esta correto
3. Verificar logs para identificar onde falhou
4. Testar provider de modelo isoladamente

### Problema: Transcricao de audio falha

**Sintoma**: Mensagens de audio nao sao processadas

**Solucoes**:
1. Verificar se `OPENAI_API_KEY` esta configurado
2. Verificar se o arquivo de audio e acessivel
3. Verificar formato do audio (deve ser compativel com Whisper)

### Problema: Cobertura de testes baixa

**Sintoma**: `pytest --cov` falha com cobertura < 85%

**Solucoes**:
1. Executar `pytest --cov=app --cov=db --cov-report=html`
2. Abrir `htmlcov/index.html` para ver o que falta cobrir
3. Adicionar testes para areas nao cobertas

## Proximos passos

Apos configurar o template:

1. **Customizar prompts**: Adapte as regras de conversa para o seu cliente
2. **Configurar departamentos**: Defina os departamentos para transferencia
3. **Testar fluxos**: Valide FAQ, qualificacao e transferencia
4. **Deploy**: Configure CI/CD e deploy em producao
5. **Monitoramento**: Configure logs e metricas

## Recursos adicionais

- [CONFIGURATION.md](./CONFIGURATION.md) - Referencia completa de configuracao
- [CUSTOMIZATION.md](./CUSTOMIZATION.md) - Guia de customizacao
- [docs/examples/](./docs/examples/) - Exemplos de configuracao
- [docs/phases/](./docs/phases/) - Documentacao de cada fase do projeto
- [docs/features/](./docs/features/) - Documentacao de cada feature

## Suporte

Para duvidas ou problemas:

1. Consulte a documentacao em `docs/`
2. Verifique issues conhecidos no repositorio
3. Entre em contato com a equipe de desenvolvimento

---

**Tempo estimado de onboarding**: 20-30 minutos

**Proximo passo**: [Customizar o template](./CUSTOMIZATION.md)
