"""Logging estruturado com correlation id para observabilidade."""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.observability.correlation import get_correlation_id

LOGGER_NAME = "app.observability"


def get_observability_logger() -> logging.Logger:
    """Retorna logger dedicado para eventos estruturados da API."""
    return logging.getLogger(LOGGER_NAME)


def log_structured(
    event: str,
    *,
    level: int = logging.INFO,
    logger: logging.Logger | None = None,
    **fields: Any,
) -> None:
    """Emite log JSON com campos base para rastreabilidade operacional."""
    active_logger = logger or get_observability_logger()
    payload: dict[str, Any] = {
        "event": event,
        "correlation_id": get_correlation_id(),
        "ts": datetime.now(tz=timezone.utc).isoformat(),
    }
    payload.update(fields)
    active_logger.log(level, json.dumps(payload, ensure_ascii=True, sort_keys=True, default=str))
