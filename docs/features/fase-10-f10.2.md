# Feature 10.2 - guia de onboarding por cliente

## Status

- Concluida.

## Objetivo

Criar documentacao completa de onboarding para facilitar a replicacao do template por novo cliente, com processo de setup claro, configuracao de variaveis de ambiente e customizacao por provider.

## Contexto

O template conversacional Agno deve ser facilmente replicavel para diferentes clientes. Esta feature documenta o processo completo de onboarding, desde o clone do repositorio ate a primeira conversa funcional, incluindo customizacao de CRM, Sender e providers de modelo.

## Requisitos

### Guia de onboarding completo

O guia deve cobrir:

1. **Pre-requisitos**
   - Docker e Docker Compose
   - Python 3.12+
   - uv (gerenciador de pacotes Python)
   - Git

2. **Setup inicial**
   - Clone do repositorio
   - Configuracao de variaveis de ambiente
   - Inicializacao do banco de dados
   - Primeira execucao

3. **Configuracao por provider**
   - CRM (Helena como default)
   - WhatsApp Sender
   - Modelo de IA (OpenAI, OpenRouter, Groq, Claude, Gemini)
   - Providers de transcricao/analise multimodal

4. **Customizacao**
   - Prompts e regras de conversa
   - Departamentos e transferencias
   - FAQ e qualificacao
   - Guardrails e limites

5. **Validacao**
   - Testes de integracao
   - Primeira conversa de teste
   - Troubleshooting comum

## Estrutura do guia

### Documento principal: `docs/ONBOARDING.md`

Guia passo a passo para novo cliente.

### Documento de configuracao: `docs/CONFIGURATION.md`

Referencia completa de todas variaveis de ambiente e opcoes de configuracao.

### Documento de customizacao: `docs/CUSTOMIZATION.md`

Guia de onde e como customizar o template para necessidades especificas do cliente.

### Exemplos de configuracao: `docs/examples/`

Exemplos prontos de configuracao para diferentes cenarios:
- `helena-openai.env.example` - Helena + OpenAI
- `helena-openrouter.env.example` - Helena + OpenRouter
- `custom-crm.env.example` - CRM customizado
- `multi-provider.env.example` - Multiplos providers

## Implementacao

### 1. Criar ONBOARDING.md

Guia principal com fluxo completo de setup.

### 2. Criar CONFIGURATION.md

Documentacao de todas variaveis de ambiente com:
- Nome da variavel
- Descricao
- Valores possiveis
- Valor default
- Obrigatoriedade
- Exemplo

### 3. Criar CUSTOMIZATION.md

Guia de customizacao com:
- Onde customizar prompts
- Como adicionar novos departamentos
- Como customizar regras de conversa
- Como trocar providers
- Como adicionar novos preprocessors

### 4. Criar exemplos de configuracao

Arquivos `.env.example` para diferentes cenarios comuns.

### 5. Adicionar secao de troubleshooting

Problemas comuns e solucoes.

## Criterios de aceitacao

- [x] `docs/ONBOARDING.md` criado com guia passo a passo completo
- [x] `docs/CONFIGURATION.md` criado com referencia de todas variaveis
- [x] `docs/CUSTOMIZATION.md` criado com guia de customizacao
- [x] `docs/examples/` criado com 5 exemplos de configuracao
- [x] Secao de troubleshooting adicionada ao ONBOARDING.md
- [x] Testes automatizados criados em `tests/test_onboarding_docs.py`
- [x] Documentacao da feature concluida

## Testes

### Automatizados

- Validar que todos arquivos de documentacao existem
- Validar que exemplos de configuracao sao validos
- Validar que todas variaveis obrigatorias estao documentadas

### Manuais

- Dry-run de onboarding em ambiente limpo
- Validar que novo desenvolvedor consegue seguir o guia
- Validar que exemplos de configuracao funcionam
- Validar que troubleshooting cobre problemas comuns

## Dependencias

- Feature 10.1 concluida (checklist de release)
- Todas fases anteriores concluidas (1-9)

## Proximos passos

Apos conclusao desta feature:
- Feature 10.3 - changelog e versionamento
- Feature 10.4 - pipeline de release
- Feature 10.5 - documentacao final de operacao

## Tempo estimado

- Criacao de documentacao: 2-3 horas
- Criacao de exemplos: 1 hora
- Validacao com novo desenvolvedor: 1 hora
- Total: 4-5 horas
