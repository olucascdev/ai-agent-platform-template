"""Dependencias FastAPI para rotas de webhook."""

from functools import lru_cache

from app.services import WhatsAppWebhookPipelineService, build_whatsapp_webhook_pipeline_service


@lru_cache(maxsize=1)
def get_whatsapp_webhook_pipeline_service() -> WhatsAppWebhookPipelineService:
    """Retorna singleton do pipeline de webhook para uso nas rotas."""
    return build_whatsapp_webhook_pipeline_service()
