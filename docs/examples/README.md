# Exemplos de Configuracao

Este diretorio contem exemplos de configuracao para diferentes cenarios de uso do template conversacional Agno.

## Exemplos disponiveis

### 1. Helena + OpenAI (`helena-openai.env.example`)

Configuracao padrao recomendada para producao:
- CRM: Helena
- Modelo: OpenAI GPT-4o-mini
- Preprocessor: OpenAI (Whisper + Vision)

**Quando usar**: Cliente novo que quer setup rapido e confiavel.

### 2. Helena + OpenRouter (`helena-openrouter.env.example`)

Configuracao com acesso a multiplos modelos:
- CRM: Helena
- Modelo: Claude 3.5 Sonnet via OpenRouter
- Preprocessor: OpenAI (Whisper + Vision)

**Quando usar**: Cliente quer flexibilidade para trocar modelos facilmente.

### 3. Helena + Groq (`helena-groq.env.example`)

Configuracao para inferencia rapida e gratuita:
- CRM: Helena
- Modelo: Llama 3.3 70B via Groq
- Preprocessor: Groq (audio) + OpenAI (imagem)

**Quando usar**: Testes, desenvolvimento ou cliente com budget limitado.

### 4. CRM Customizado (`custom-crm.env.example`)

Configuracao para CRM proprio do cliente:
- CRM: Customizado (requer adapter)
- Modelo: OpenAI GPT-4o-mini
- Sender: Customizado (requer adapter)

**Quando usar**: Cliente tem CRM/Sender proprio e nao usa Helena.

### 5. Producao (`production.env.example`)

Configuracao otimizada para producao:
- Banco: Supabase
- CRM: Helena
- Modelo: OpenAI GPT-4o-mini
- Observabilidade completa
- Seguranca configurada

**Quando usar**: Deploy em producao com alta disponibilidade.

## Como usar

1. **Escolha o exemplo** que mais se aproxima do seu cenario
2. **Copie o arquivo** para `.env` na raiz do projeto:
   ```bash
   cp docs/examples/helena-openai.env.example .env
   ```
3. **Edite o arquivo** `.env` e preencha os valores reais:
   - Tokens de API
   - URLs de servicos
   - Credenciais de banco
4. **Valide a configuracao**:
   ```bash
   python scripts/pre_release_check.py
   ```
5. **Suba a aplicacao**:
   ```bash
   docker compose up -d
   ```

## Customizacao adicional

Para customizacoes mais avancadas, consulte:

- [CONFIGURATION.md](../CONFIGURATION.md) - Referencia completa de variaveis
- [CUSTOMIZATION.md](../CUSTOMIZATION.md) - Guia de customizacao
- [ONBOARDING.md](../ONBOARDING.md) - Guia de setup inicial

## Matriz de compatibilidade

| Exemplo | CRM | Modelo | Audio | Imagem | Producao |
|---------|-----|--------|-------|--------|----------|
| helena-openai | Helena | OpenAI | OpenAI | OpenAI | ✅ |
| helena-openrouter | Helena | OpenRouter | OpenAI | OpenAI | ✅ |
| helena-groq | Helena | Groq | Groq | OpenAI | ⚠️ |
| custom-crm | Custom | OpenAI | OpenAI | OpenAI | ✅ |
| production | Helena | OpenAI | OpenAI | OpenAI | ✅ |

Legenda:
- ✅ Recomendado para producao
- ⚠️ Recomendado apenas para desenvolvimento/testes

## Suporte

Para duvidas sobre configuracao:

1. Consulte a documentacao em `docs/`
2. Verifique o troubleshooting em `docs/ONBOARDING.md`
3. Entre em contato com a equipe de desenvolvimento
