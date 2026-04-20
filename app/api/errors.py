"""Padrao de erro observavel e auditavel para toda a API."""

from datetime import datetime, timezone
import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models import ApiErrorDetail, ApiErrorResponse
from app.observability import get_correlation_id, log_structured

CORRELATION_ID_HEADER = "X-Correlation-Id"


class ApiApplicationError(RuntimeError):
    """Erro de dominio HTTP com status/code controlados pela aplicacao."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def register_exception_handlers(app: FastAPI) -> None:
    """Registra handlers globais com envelope unico de erro."""

    @app.exception_handler(ApiApplicationError)
    async def handle_api_application_error(request: Request, exc: ApiApplicationError) -> JSONResponse:
        return _build_error_response(
            request=request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            error_type=exc.__class__.__name__,
            details=exc.details,
            log_level=logging.WARNING,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _build_error_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="request.validation_error",
            message="Request payload validation failed.",
            error_type=exc.__class__.__name__,
            details=exc.errors(),
            log_level=logging.WARNING,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return _build_error_response(
            request=request,
            status_code=exc.status_code,
            code=f"http.{exc.status_code}",
            message=str(exc.detail),
            error_type=exc.__class__.__name__,
            details=exc.detail,
            log_level=logging.WARNING,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        return _build_error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal.unexpected_error",
            message="Unexpected server error.",
            error_type=exc.__class__.__name__,
            details=None,
            log_level=logging.ERROR,
        )


def _build_error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    error_type: str,
    details: Any | None,
    log_level: int,
) -> JSONResponse:
    correlation_id = _resolve_correlation_id(request)
    sanitized_details = _sanitize_details(details)
    error_payload = ApiErrorResponse(
        status="error",
        error=ApiErrorDetail(
            code=code,
            message=message,
            error_type=error_type,
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
            ts=datetime.now(tz=timezone.utc).isoformat(),
            details=sanitized_details,
        ),
    )
    log_structured(
        "api_error_response",
        level=log_level,
        correlation_id=correlation_id,
        status_code=status_code,
        error_code=code,
        error_type=error_type,
        message=message,
        path=request.url.path,
        method=request.method,
    )

    response = JSONResponse(status_code=status_code, content=error_payload.model_dump(exclude_none=True))
    if correlation_id is not None:
        response.headers[CORRELATION_ID_HEADER] = correlation_id
    return response


def _sanitize_details(details: Any | None) -> Any | None:
    if details is None:
        return None

    return jsonable_encoder(details, custom_encoder={Exception: lambda value: str(value)})


def _resolve_correlation_id(request: Request) -> str | None:
    from_context = get_correlation_id()
    if from_context is not None:
        return from_context

    from_state = getattr(request.state, "correlation_id", None)
    if isinstance(from_state, str) and from_state.strip():
        return from_state.strip()

    return None
