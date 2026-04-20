"""Schemas tipados de entrada e saida da API."""

from app.models.error import ApiErrorDetail, ApiErrorResponse
from app.models.webhook import WhatsAppWebhookAcceptedResponse, WhatsAppWebhookRequest

__all__ = [
    "ApiErrorDetail",
    "ApiErrorResponse",
    "WhatsAppWebhookAcceptedResponse",
    "WhatsAppWebhookRequest",
]
