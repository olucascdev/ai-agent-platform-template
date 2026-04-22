# Tutorial dos Prompts

Este diretorio guarda os arquivos de prompt usados pelo agente.

O carregador junta os arquivos nesta ordem:

1. `identity.md`
2. `departments.md`
3. `objections.md`
4. `faq.md`
5. `flow_steps.md`

Essa ordem e importante porque define contexto geral primeiro e regras de execucao por ultimo.

## Variaveis por cliente (novo)

Agora o template suporta placeholders e perfil por cliente sem alterar codigo.

### 1) Placeholders nos arquivos `.md`

Use sintaxe `{{nome_da_variavel}}` dentro dos prompts.

Exemplo em `identity.md`:

`Voce e {{agent_persona_name}}, da {{business_name}}.`

No `.env`, informe:

`PROMPT_CONTEXT_JSON={"agent_persona_name":"Nathalia","business_name":"BM Odontologia"}`

Se faltar alguma variavel usada no prompt, o carregamento falha com erro explicito.

### 2) Perfil de cliente com override de arquivos

Voce pode criar uma pasta com prompts especificos do cliente:

`prompts/clients/<PROMPT_CLIENT_KEY>/`

Exemplo:

- `prompts/clients/brunomachado/identity.md`
- `prompts/clients/brunomachado/faq.md`

No `.env`:

`PROMPT_CLIENT_KEY=brunomachado`

Regra de carregamento:

- Se existir arquivo no perfil do cliente, ele substitui o arquivo base.
- Se nao existir, usa o arquivo base de `prompts/`.

## Contexto dinamico por mensagem (estilo n8n)

Alem dos `.md`, o pipeline injeta um bloco dinamico antes da mensagem principal com dados do evento:

- nome (quando existir)
- telefone
- session_id
- horario atual
- categoria do cliente (opcional)

Variaveis de ambiente relacionadas:

- `AGENT_TIMEZONE` (default: `America/Sao_Paulo`)
- `AGENT_CUSTOMER_TIER` (opcional, ex.: `diamante`)

Esse bloco e gerado em runtime e nao precisa ser escrito manualmente no n8n.

## Para que serve cada arquivo

### `identity.md`

Define quem o agente e, tom de voz, missao e limites.

Use para:

- identidade da persona (ex.: Nathalia)
- estilo de resposta (curto, empatico, objetivo)
- proibicoes globais (ex.: nao falar preco)

### `departments.md`

Define regras de roteamento e transferencia para humano/areas.

Use para:

- mapear departamentos e IDs reais
- definir quando transferir
- definir como transferir (silencioso, sem avisar cliente)

### `objections.md`

Biblioteca de objecoes e respostas aprovadas.

Use para:

- padronizar resposta para duvidas sensiveis
- manter consistencia comercial
- orientar proxima acao (continuar conversa ou handoff)

### `faq.md`

Base de conhecimento operacional do negocio.

Use para:

- horarios, localizacao, regras da clinica
- servicos, restricoes e politicas
- respostas factuais que nao devem variar

### `flow_steps.md`

Define o fluxo conversacional e os gates entre etapas.

Use para:

- ordem dos passos (acolhimento, necessidade, agendamento)
- criterios de passagem entre steps
- regras especiais (ex.: modo `[ATIVACAO]`)

## Como editar sem quebrar o comportamento

- Mantenha os nomes dos arquivos iguais.
- Mantenha linguagem clara, curta e sem contradicoes.
- Evite duplicar regra em varios arquivos com textos diferentes.
- Quando mudar politica critica (preco, transferencia, agenda), atualize `identity.md`, `faq.md` e `flow_steps.md` em conjunto.

## Checklist rapido antes de testar

- `identity.md` define tom e proibicoes?
- `departments.md` tem IDs reais?
- `objections.md` cobre as principais objecoes?
- `faq.md` esta atualizado com dados reais?
- `flow_steps.md` bloqueia pulo de etapa e define handoff?

Se todos os itens estiverem ok, o agente ja pode ser validado em testes reais de conversa.
