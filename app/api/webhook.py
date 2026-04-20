"""Rotas HTTP de webhook para entrada de eventos do WhatsApp."""

import logging

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_whatsapp_webhook_pipeline_service
from app.api.errors import ApiApplicationError
from app.models.webhook import (
    WhatsAppWebhookAcceptedResponse,
    WhatsAppWebhookRequest,
    WhatsAppWebhookWrappedPayload,
)
from app.observability import log_structured
from app.preprocessing import EventNormalizationError
from app.services import WhatsAppWebhookPipelineService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post(
    "/whatsapp",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=WhatsAppWebhookAcceptedResponse,
)
async def receive_whatsapp_webhook(
    payload: WhatsAppWebhookRequest,
    pipeline_service: WhatsAppWebhookPipelineService = Depends(get_whatsapp_webhook_pipeline_service),
) -> WhatsAppWebhookAcceptedResponse:
    """Executa pipeline E2E com dependencia injetada para facilitar testes."""
    event_payload = payload.event_payload()
    raw_event_payload = event_payload.model_dump(by_alias=True, exclude_none=True)
    log_structured(
        "webhook_whatsapp_received",
        event_id=event_payload.event_id,
        message_id=getattr(event_payload.last_message, "id", None),
        has_wrapper=isinstance(payload.root, WhatsAppWebhookWrappedPayload),
    )

    try:
        pipeline_result = await pipeline_service.process(raw_event_payload)
    except EventNormalizationError as exc:
        log_structured(
            "webhook_whatsapp_rejected",
            level=logging.WARNING,
            error_type=exc.__class__.__name__,
            detail=str(exc),
        )
        raise ApiApplicationError(
            code="webhook.normalization_error",
            message="Webhook event normalization failed.",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details={"reason": str(exc)},
        ) from exc

    log_structured(
        "webhook_whatsapp_accepted",
        event_id=pipeline_result.event_id,
        message_id=pipeline_result.normalized_event.message_id,
        is_duplicate=pipeline_result.is_duplicate,
        session_command=pipeline_result.session_command,
    )

    return WhatsAppWebhookAcceptedResponse(
        status="accepted",
        session_id=pipeline_result.normalized_event.session_id,
        contact_phone=pipeline_result.normalized_event.contact_phone,
        message_id=pipeline_result.normalized_event.message_id,
        event_id=pipeline_result.event_id,
        is_duplicate=pipeline_result.is_duplicate,
        session_command=pipeline_result.session_command,
    )
