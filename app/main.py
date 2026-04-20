"""Ponto de entrada da API FastAPI do template conversacional."""

from os import getenv

import uvicorn
from fastapi import FastAPI

from app.api import webhook_router
from app.config import settings

app = FastAPI(
    title="Agno Conversational Template",
    description=f"API base para evoluir o webhook conversacional por fases. Agente: {settings.agent_name}.",
    version="1.0.0",
)

app.include_router(webhook_router)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Endpoint simples para validar se a API esta ativa."""
    return {"status": "ok"}


if __name__ == "__main__":
    runtime_env = getenv("RUNTIME_ENV", "prd")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=(runtime_env == "dev"))
