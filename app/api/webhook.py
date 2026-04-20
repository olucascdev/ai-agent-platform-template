"""Rotas HTTP de webhook para entrada de eventos do WhatsApp."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_whatsapp_webhook_pipeline_service
from app.models.webhook import WhatsAppWebhookAcceptedResponse, WhatsAppWebhookRequest
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

    try:
        pipeline_result = await pipeline_service.process(raw_event_payload)
    except EventNormalizationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return WhatsAppWebhookAcceptedResponse(
        status="accepted",
        session_id=pipeline_result.normalized_event.session_id,
        contact_phone=pipeline_result.normalized_event.contact_phone,
        message_id=pipeline_result.normalized_event.message_id,
        event_id=pipeline_result.event_id,
        is_duplicate=pipeline_result.is_duplicate,
        session_command=pipeline_result.session_command,
    )
