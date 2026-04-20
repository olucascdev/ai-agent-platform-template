"""Exporta modelos de banco usados pela aplicacao."""

from db.models.lead import Lead
from db.models.webhook_event import ProcessedWebhookEvent

__all__ = ["Lead", "ProcessedWebhookEvent"]
