"""Schemas de erro padronizados para respostas HTTP auditaveis."""

from typing import Any, Literal

from pydantic import BaseModel


class ApiErrorDetail(BaseModel):
    """Payload estruturado com metadados essenciais de erro."""

    code: str
    message: str
    error_type: str
    correlation_id: str | None = None
    path: str
    method: str
    ts: str
    details: Any | None = None


class ApiErrorResponse(BaseModel):
    """Envelope padrao para erros de API."""

    status: Literal["error"]
    error: ApiErrorDetail
