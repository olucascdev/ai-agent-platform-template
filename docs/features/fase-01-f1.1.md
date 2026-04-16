# Fase 1 - Feature 1.1

## O que foi feito

- Atualizado `pyproject.toml` com dependencias de runtime pinadas para o template conversacional.
- Removidas dependencias do template demo que nao fazem parte do escopo alvo.
- Definido conjunto minimo de libs para API, banco, LLM, multimodal, migracao e configuracao.

## Dependencias fixadas

- `agno==2.5.5`
- `fastapi==0.134.0`
- `uvicorn[standard]==0.41.0`
- `sqlalchemy[asyncio]==2.0.47`
- `asyncpg==0.30.0`
- `httpx==0.28.1`
- `openai==2.24.0`
- `google-generativeai==0.8.5`
- `python-dotenv==1.2.1`
- `alembic==1.16.5`
- `pydantic-settings==2.13.1`

## Teste da feature

- Criado `tests/test_dependencies.py` para validar que a lista de dependencias permanece exatamente pinada conforme o contrato da fase.
