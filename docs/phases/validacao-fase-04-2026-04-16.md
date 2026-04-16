# Validacao automatizada - fase 4 (2026-04-16)

## Escopo

- Validar features 4.1 a 4.6 da fase 4.
- Executar gate de qualidade completo do repositorio apos as mudancas.
- Deixar trilha pronta para validacao manual do time.

## Ambiente

- Repositorio: `ai-agent-platform-template`
- Data: `2026-04-16`
- Ferramentas: `uv`, `pytest`, `ruff`, `mypy`

## Execucao automatizada (IA)

1. Sincronizacao de dependencias

   - Comando: `uv sync --extra dev`
   - Resultado: sucesso (`Resolved 84 packages`, `Checked 82 packages`)

2. Suite dedicada da fase 4

   - Comando:
     - `uv run python -m pytest -q tests/test_http_client.py tests/test_crm_client.py tests/test_whatsapp_sender_client.py tests/test_retry_policy.py tests/test_integrations_simulated.py tests/test_contracts.py tests/test_config.py tests/test_env_example.py`
   - Resultado: `38 passed in 0.28s`

3. Regressao completa do projeto

   - Comando: `uv run python -m pytest -q`
   - Resultado: `61 passed in 0.42s`

4. Gate de qualidade

   - `uv run python -m ruff check .` -> `All checks passed!`
   - `uv run python -m mypy .` -> `Success: no issues found in 40 source files`

## Conclusao automatizada

- Validacao automatizada da fase 4 concluida com sucesso.
- Features 4.1 a 4.6 aprovadas em testes dedicados.
- Gate global do projeto aprovado (testes, lint e tipagem).

## Execucao manual (time)

1. Conferencia de configuracoes

   - Resultado:
     - `crm_base_url`: `https://seu-crm.exemplo.com/api/v1`
     - `sender_url`: `https://seu-sender.exemplo.com/send/text`
   - Observacao: ambiente ainda com URLs placeholder de exemplo.

2. Lookup no CRM

   - Comando executado: smoke de `find_contact_by_phone`
   - Resultado: falha com `HttpClientResponseError`
   - Detalhe: `GET https://seu-crm.exemplo.com/api/v1/contacts -> status=410`

3. Transferencia no CRM

   - Comando executado: smoke de `transfer_contact`
   - Resultado: falha com `HttpClientResponseError`
   - Detalhe: `POST https://seu-crm.exemplo.com/api/v1/contacts/contact-id-real/ticket/transfer -> status=410`

4. Envio no sender WhatsApp

   - Comando executado: smoke de `send_text`
   - Resultado: falha com `HttpClientResponseError`
   - Detalhe: `POST https://seu-sender.exemplo.com/send/text -> status=410`

5. Guardrails de validacao de entrada

   - Telefone vazio: `ValueError` conforme esperado.
   - Texto vazio: `ValueError` conforme esperado.

## Diagnostico da execucao manual

- As falhas manuais nao indicam bug do codigo da fase 4.
- O erro `410` ocorre porque o ambiente usa endpoints placeholder (`seu-crm.exemplo.com` e `seu-sender.exemplo.com`).
- A validacao de guardrails confirmou comportamento correto de validacao de entrada.
- Aviso de `VIRTUAL_ENV` divergente do `uv` foi observado e nao impactou os resultados.

### Comandos recomendados para validacao manual

1. Conferir configuracoes carregadas

```bash
uv run python - <<'PY'
from app.config import settings
print({
    "crm_base_url": settings.crm_base_url,
    "crm_lookup_path": settings.crm_contacts_lookup_path,
    "crm_transfer_path_template": settings.crm_transfer_path_template,
    "sender_url": settings.whatsapp_sender_url,
    "sender_method": settings.whatsapp_sender_method,
    "sender_number_field": settings.whatsapp_sender_number_field,
    "sender_text_field": settings.whatsapp_sender_text_field,
    "http_timeout_seconds": settings.http_timeout_seconds,
    "http_max_retries": settings.http_max_retries,
    "http_retry_backoff_seconds": settings.http_retry_backoff_seconds,
})
PY
```

2. Smoke manual de lookup no CRM

```bash
export TEST_PHONE="+5531999999999"

uv run python - <<'PY'
import asyncio, os
from app.integrations import build_crm_client

async def main():
    client = build_crm_client()
    contact = await client.find_contact_by_phone(os.environ["TEST_PHONE"])
    if contact is None:
        print("Contato nao encontrado")
    else:
        print("Contato encontrado:", contact.contact_id)

asyncio.run(main())
PY
```

3. Smoke manual de transferencia no CRM

```bash
export TEST_CONTACT_ID="contact-id-real"
export TEST_DEPARTMENT_ID="department-id-real"
export TEST_COMMENTS="Teste manual fase 4"

uv run python - <<'PY'
import asyncio, os
from app.integrations import build_crm_client

async def main():
    client = build_crm_client()
    payload = await client.transfer_contact(
        contact_id=os.environ["TEST_CONTACT_ID"],
        department_id=os.environ["TEST_DEPARTMENT_ID"],
        comments=os.environ["TEST_COMMENTS"],
    )
    print("Transferencia:", payload)

asyncio.run(main())
PY
```

4. Smoke manual de envio no sender WhatsApp

```bash
export TEST_PHONE="+5531999999999"
export TEST_TEXT="Teste manual sender fase 4"

uv run python - <<'PY'
import asyncio, os
from app.integrations import build_whatsapp_sender_client

async def main():
    client = build_whatsapp_sender_client()
    result = await client.send_text(
        phone=os.environ["TEST_PHONE"],
        text=os.environ["TEST_TEXT"],
    )
    print("Envio:", result.status_code, result.payload)

asyncio.run(main())
PY
```

5. Guardrail manual de validacao de entrada

```bash
uv run python - <<'PY'
import asyncio
from app.integrations import build_whatsapp_sender_client

async def main():
    client = build_whatsapp_sender_client()
    try:
        await client.send_text(phone="   ", text="msg")
    except Exception as exc:
        print(type(exc).__name__, str(exc))

asyncio.run(main())
PY
```

## Checklist de fechamento manual

- [ ] Lookup CRM validado (pendente de URL/token reais).
- [ ] Transferencia CRM validada (pendente de URL/token reais).
- [ ] Envio sender validado (pendente de URL/token reais).
- [x] Guardrails de validacao conferidos.

## Proximo passo para fechamento manual

Atualizar `.env` com endpoints e credenciais reais de CRM/Sender e reexecutar os passos 2, 3 e 4 desta secao.
