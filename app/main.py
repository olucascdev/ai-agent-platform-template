"""Ponto de entrada da API FastAPI do template conversacional."""

from time import perf_counter
from os import getenv

import uvicorn
from fastapi import FastAPI, Request

from app.api import webhook_router
from app.config import settings
from app.observability import (
    log_structured,
    reset_correlation_id,
    resolve_correlation_id,
    set_correlation_id,
)

CORRELATION_ID_HEADER = "X-Correlation-Id"

app = FastAPI(
    title="Agno Conversational Template",
    description=f"API base para evoluir o webhook conversacional por fases. Agente: {settings.agent_name}.",
    version="1.0.0",
)

app.include_router(webhook_router)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Aplica correlation id para request/response e log estruturado de acesso."""
    correlation_id = resolve_correlation_id(request.headers.get(CORRELATION_ID_HEADER))
    request.state.correlation_id = correlation_id
    correlation_token = set_correlation_id(correlation_id)
    started_at = perf_counter()

    response = None
    raised_error_type: str | None = None
    try:
        response = await call_next(request)
    except Exception as exc:
        raised_error_type = exc.__class__.__name__
        raise
    finally:
        duration_ms = int((perf_counter() - started_at) * 1000)
        log_structured(
            "http_request_completed",
            method=request.method,
            path=request.url.path,
            status_code=getattr(response, "status_code", 500),
            error_type=raised_error_type,
            duration_ms=duration_ms,
        )
        reset_correlation_id(correlation_token)

    if response is None:
        raise RuntimeError("Middleware HTTP finalizada sem resposta valida.")

    response.headers[CORRELATION_ID_HEADER] = correlation_id
    return response


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Endpoint simples para validar se a API esta ativa."""
    return {"status": "ok"}


if __name__ == "__main__":
    runtime_env = getenv("RUNTIME_ENV", "prd")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=(runtime_env == "dev"))
