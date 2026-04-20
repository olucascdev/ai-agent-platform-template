# Guia de Customizacao - Template Conversacional Agno

Este guia mostra onde e como customizar o template para as necessidades especificas do seu cliente.

## Indice

- [Prompts e Regras de Conversa](#prompts-e-regras-de-conversa)
- [Departamentos e Transferencias](#departamentos-e-transferencias)
- [FAQ e Qualificacao](#faq-e-qualificacao)
- [Guardrails e Limites](#guardrails-e-limites)
- [Integracoes (CRM e Sender)](#integracoes-crm-e-sender)
- [Preprocessor Multimodal](#preprocessor-multimodal)
- [Provider de Modelo](#provider-de-modelo)

---

## Prompts e Regras de Conversa

### Onde customizar

Os prompts sao carregados de forma modular pela funcao `load_prompt()` em `app/config.py`.

### Estrutura de prompts

```
prompts/
├── base.txt              # Prompt base do agente
├── rules.txt             # Regras de conversa
├── faq.txt              # Perguntas frequentes
├── qualification.txt     # Regras de qualificacao
└── handoff.txt          # Regras de transferencia
```

### Como customizar

1. **Criar diretorio de prompts**:
   ```bash
   mkdir -p prompts
   ```

2. **Criar prompt base** (`prompts/base.txt`):
   ```text
   Voce e um assistente virtual da [NOME_EMPRESA].
   Seu objetivo e ajudar clientes com informacoes sobre [PRODUTOS/SERVICOS].
   
   Seja sempre educado, claro e objetivo.
   ```

3. **Criar regras de conversa** (`prompts/rules.txt`):
   ```text
   REGRAS DE CONVERSA:
   
   1. Sempre cumprimente o cliente na primeira mensagem
   2. Identifique a intencao do cliente (informacao, compra, suporte)
   3. Responda de forma clara e objetiva
   4. Se nao souber a resposta, transfira para humano
   5. Sempre se despeca ao final da conversa
   ```

4. **Configurar carregamento**:
   
   Edite `app/config.py` para apontar para seus prompts customizados:
   
   ```python
   def load_prompt(self) -> str:
       """Carrega prompt modular do agente."""
       parts = []
       
       # Prompt base
       base_path = Path("prompts/base.txt")
       if base_path.exists():
           parts.append(base_path.read_text())
       
       # Regras
       rules_path = Path("prompts/rules.txt")
       if rules_path.exists():
           parts.append(rules_path.read_text())
       
       # FAQ
       faq_path = Path("prompts/faq.txt")
       if faq_path.exists():
           parts.append(faq_path.read_text())
       
       return "\n\n".join(parts)
   ```

### Exemplo de prompt completo

```text
Voce e Maria, assistente virtual da Loja XYZ.

OBJETIVO:
Ajudar clientes com informacoes sobre produtos, precos e disponibilidade.

REGRAS:
1. Sempre cumprimente o cliente pelo nome (se disponivel)
2. Identifique se o cliente quer: informacao, compra ou suporte
3. Seja breve e objetivo (maximo 3 paragrafos)
4. Use emojis com moderacao
5. Sempre pergunte se pode ajudar em mais alguma coisa

FAQ:
Q: Qual o horario de funcionamento?
A: Funcionamos de segunda a sexta, das 9h as 18h.

Q: Qual o prazo de entrega?
A: Entregamos em ate 5 dias uteis para todo o Brasil.

TRANSFERENCIA:
Se o cliente pedir para falar com humano, transfira para departamento "vendas".
Se houver problema tecnico, transfira para departamento "suporte".
```

---

## Departamentos e Transferencias

### Onde customizar

Edite `app/agent/handoff_comments.py` para definir departamentos e regras de transferencia.

### Como customizar

1. **Definir departamentos**:
   ```python
   DEPARTMENTS = {
       "vendas": {
           "id": "dept_vendas_001",
           "name": "Vendas",
           "description": "Equipe de vendas e orcamentos"
       },
       "suporte": {
           "id": "dept_suporte_001",
           "name": "Suporte Tecnico",
           "description": "Equipe de suporte tecnico"
       },
       "financeiro": {
           "id": "dept_financeiro_001",
           "name": "Financeiro",
           "description": "Equipe financeira e cobrancas"
       }
   }
   ```

2. **Definir regras de transferencia**:
   ```python
   def should_transfer_to_human(message: str, context: dict) -> tuple[bool, str | None]:
       """
       Determina se deve transferir para humano.
       
       Returns:
           (should_transfer, department_id)
       """
       message_lower = message.lower()
       
       # Cliente pede explicitamente
       if any(word in message_lower for word in ["humano", "atendente", "pessoa"]):
           return True, DEPARTMENTS["vendas"]["id"]
       
       # Problema tecnico
       if any(word in message_lower for word in ["erro", "bug", "nao funciona"]):
           return True, DEPARTMENTS["suporte"]["id"]
       
       # Questao financeira
       if any(word in message_lower for word in ["pagamento", "boleto", "fatura"]):
           return True, DEPARTMENTS["financeiro"]["id"]
       
       return False, None
   ```

3. **Gerar comments estruturados**:
   ```python
   def generate_handoff_comments(
       lead_name: str,
       conversation_history: list[dict],
       reason: str
   ) -> str:
       """Gera comments estruturados para handoff."""
       return f"""
   TRANSFERENCIA AUTOMATICA
   
   Cliente: {lead_name}
   Motivo: {reason}
   
   HISTORICO DA CONVERSA:
   {format_conversation(conversation_history)}
   
   PROXIMOS PASSOS SUGERIDOS:
   - Revisar historico completo
   - Identificar necessidade especifica
   - Responder em ate 5 minutos
   """
   ```

---

## FAQ e Qualificacao

### Onde customizar

Edite `app/agent/conversation_rules.py` para definir FAQ e regras de qualificacao.

### Como customizar FAQ

1. **Criar arquivo de FAQ** (`prompts/faq.txt`):
   ```text
   PERGUNTAS FREQUENTES:
   
   Q: Qual o horario de funcionamento?
   A: Funcionamos de segunda a sexta, das 9h as 18h.
   
   Q: Qual o prazo de entrega?
   A: Entregamos em ate 5 dias uteis.
   
   Q: Quais formas de pagamento?
   A: Aceitamos cartao, PIX e boleto.
   ```

2. **Implementar deteccao de FAQ**:
   ```python
   def detect_faq_intent(message: str) -> str | None:
       """Detecta se mensagem e uma pergunta frequente."""
       message_lower = message.lower()
       
       if "horario" in message_lower or "funciona" in message_lower:
           return "horario_funcionamento"
       
       if "entrega" in message_lower or "prazo" in message_lower:
           return "prazo_entrega"
       
       if "pagamento" in message_lower or "pagar" in message_lower:
           return "formas_pagamento"
       
       return None
   ```

### Como customizar qualificacao

1. **Definir criterios de qualificacao**:
   ```python
   def qualify_lead(conversation: list[dict]) -> dict:
       """Qualifica lead baseado na conversa."""
       score = 0
       signals = []
       
       for msg in conversation:
           content = msg["content"].lower()
           
           # Sinais de interesse
           if any(word in content for word in ["quero", "gostaria", "preciso"]):
               score += 10
               signals.append("interesse_expresso")
           
           # Perguntou sobre preco
           if any(word in content for word in ["preco", "valor", "quanto"]):
               score += 15
               signals.append("perguntou_preco")
           
           # Perguntou sobre disponibilidade
           if any(word in content for word in ["disponivel", "estoque", "tem"]):
               score += 10
               signals.append("perguntou_disponibilidade")
       
       return {
           "score": score,
           "signals": signals,
           "qualified": score >= 20
       }
   ```

2. **Usar qualificacao no agente**:
   ```python
   qualification = qualify_lead(conversation_history)
   
   if qualification["qualified"]:
       # Lead qualificado - priorizar atendimento
       priority = "high"
   else:
       priority = "normal"
   ```

---

## Guardrails e Limites

### Onde customizar

Edite `app/agent/guardrails.py` para definir limites e restricoes.

### Como customizar

1. **Definir limites de resposta**:
   ```python
   GUARDRAILS = {
       "max_response_length": 500,  # caracteres
       "max_messages_per_session": 50,
       "session_timeout_minutes": 30,
       "forbidden_topics": [
           "politica",
           "religiao",
           "conteudo_adulto"
       ]
   }
   ```

2. **Implementar validacao**:
   ```python
   def validate_response(response: str) -> tuple[bool, str]:
       """Valida resposta do agente."""
       
       # Tamanho maximo
       if len(response) > GUARDRAILS["max_response_length"]:
           return False, "Resposta muito longa"
       
       # Topicos proibidos
       response_lower = response.lower()
       for topic in GUARDRAILS["forbidden_topics"]:
           if topic in response_lower:
               return False, f"Topico proibido: {topic}"
       
       return True, "OK"
   ```

3. **Aplicar guardrails**:
   ```python
   response = agent.run(message)
   
   is_valid, reason = validate_response(response)
   if not is_valid:
       response = "Desculpe, nao posso responder sobre isso. Posso ajudar em outra coisa?"
   ```

---

## Integracoes (CRM e Sender)

### Como trocar CRM

1. **Configurar variaveis de ambiente**:
   ```env
   CRM_BASE_URL=https://api.seu-crm.com
   CRM_API_TOKEN=seu-token
   CRM_TIMEOUT=30
   ```

2. **Criar adapter customizado** (se necessario):
   
   Edite `app/integrations/crm_client.py`:
   
   ```python
   class CustomCRMAdapter:
       """Adapter para CRM customizado."""
       
       async def get_contact(self, phone: str) -> dict:
           """Busca contato no CRM."""
           response = await self.client.get(
               f"/contacts/search",
               params={"phone": phone}
           )
           return self._parse_contact(response)
       
       async def create_contact(self, data: dict) -> dict:
           """Cria contato no CRM."""
           response = await self.client.post(
               "/contacts",
               json=self._format_contact(data)
           )
           return self._parse_contact(response)
       
       def _parse_contact(self, response: dict) -> dict:
           """Converte resposta do CRM para formato interno."""
           return {
               "id": response["contact_id"],
               "name": response["full_name"],
               "phone": response["phone_number"],
               "email": response.get("email_address")
           }
       
       def _format_contact(self, data: dict) -> dict:
           """Converte formato interno para formato do CRM."""
           return {
               "full_name": data["name"],
               "phone_number": data["phone"],
               "email_address": data.get("email")
           }
   ```

### Como trocar Sender

1. **Configurar variaveis de ambiente**:
   ```env
   WHATSAPP_SENDER_BASE_URL=https://api.seu-sender.com
   WHATSAPP_SENDER_API_TOKEN=seu-token
   WHATSAPP_SENDER_TIMEOUT=30
   ```

2. **Criar adapter customizado** (se necessario):
   
   Edite `app/integrations/whatsapp_sender_client.py`:
   
   ```python
   class CustomSenderAdapter:
       """Adapter para sender customizado."""
       
       async def send_message(
           self,
           phone: str,
           message: str,
           media_url: str | None = None
       ) -> dict:
           """Envia mensagem via WhatsApp."""
           payload = {
               "to": phone,
               "text": message
           }
           
           if media_url:
               payload["media"] = {"url": media_url}
           
           response = await self.client.post(
               "/messages/send",
               json=payload
           )
           
           return {
               "message_id": response["id"],
               "status": response["status"]
           }
   ```

---

## Preprocessor Multimodal

### Como customizar transcricao de audio

Edite `app/preprocessing/audio_transcription.py`:

```python
async def transcribe_audio(audio_url: str, provider: str = "openai") -> str:
    """Transcreve audio para texto."""
    
    if provider == "openai":
        return await transcribe_with_openai(audio_url)
    elif provider == "groq":
        return await transcribe_with_groq(audio_url)
    elif provider == "assemblyai":
        return await transcribe_with_assemblyai(audio_url)
    else:
        raise ValueError(f"Provider nao suportado: {provider}")
```

### Como customizar analise de imagem

Edite `app/preprocessing/image_analysis.py`:

```python
async def analyze_image(image_url: str, provider: str = "openai") -> str:
    """Analisa imagem e extrai contexto."""
    
    prompt = """
    Analise esta imagem e descreva:
    1. O que voce ve na imagem
    2. Texto visivel (se houver)
    3. Contexto relevante para atendimento ao cliente
    """
    
    if provider == "openai":
        return await analyze_with_openai(image_url, prompt)
    elif provider == "anthropic":
        return await analyze_with_anthropic(image_url, prompt)
    else:
        raise ValueError(f"Provider nao suportado: {provider}")
```

---

## Provider de Modelo

### Como trocar provider

Basta configurar as variaveis de ambiente:

**OpenAI**:
```env
AGENT_MODEL_PROVIDER=openai
AGENT_MODEL_ID=gpt-4o-mini
AGENT_MODEL_API_KEY=sk-...
```

**OpenRouter**:
```env
AGENT_MODEL_PROVIDER=openrouter
AGENT_MODEL_ID=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=sk-or-v1-...
```

**Groq**:
```env
AGENT_MODEL_PROVIDER=groq
AGENT_MODEL_ID=llama-3.3-70b-versatile
GROQ_API_KEY=gsk_...
```

**Claude (Anthropic)**:
```env
AGENT_MODEL_PROVIDER=claude
AGENT_MODEL_ID=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

**Gemini (Google)**:
```env
AGENT_MODEL_PROVIDER=gemini
AGENT_MODEL_ID=gemini-1.5-pro
AGENT_MODEL_API_KEY=...
```

### Como adicionar novo provider

1. **Editar `app/agent/factory.py`**:
   ```python
   def create_agent(settings: Settings) -> Agent:
       """Cria agente com provider configurado."""
       
       if settings.agent_model_provider == "novo_provider":
           return create_novo_provider_agent(settings)
       # ... outros providers
   ```

2. **Implementar adapter**:
   ```python
   def create_novo_provider_agent(settings: Settings) -> Agent:
       """Cria agente com novo provider."""
       client = NovoProviderClient(
           api_key=settings.novo_provider_api_key,
           model=settings.agent_model_id
       )
       
       return Agent(
           client=client,
           prompt=settings.load_prompt()
       )
   ```

---

## Checklist de customizacao

Antes de colocar em producao, valide:

- [ ] Prompts customizados e testados
- [ ] Departamentos configurados corretamente
- [ ] FAQ cobre perguntas comuns do cliente
- [ ] Regras de qualificacao definidas
- [ ] Guardrails configurados
- [ ] CRM integrado e testado
- [ ] Sender integrado e testado
- [ ] Provider de modelo configurado
- [ ] Preprocessor multimodal testado
- [ ] Fluxo completo validado end-to-end

---

## Proximos passos

- [Voltar ao Onboarding](./ONBOARDING.md)
- [Ver configuracoes disponiveis](./CONFIGURATION.md)
- [Ver exemplos de configuracao](./examples/)
