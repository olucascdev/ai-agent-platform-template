"""Orquestracao do pipeline E2E do webhook WhatsApp."""

from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from typing import Protocol

from app.agent import apply_response_guardrails, build_agent_factory
from app.agent.session import build_single_client_session_id
from app.core.lead_service import LeadService
from app.core.webhook_idempotency_service import IdempotencyDecision, WebhookIdempotencyService
from app.integrations import (
    build_crm_client,
    build_whatsapp_sender_client,
)
from app.preprocessing import (
    NormalizedIncomingEvent,
    ResilientPreprocessingResult,
    normalize_incoming_event,
    preprocess_event_with_fallback,
)
from app.services.session_commands import SessionCommand, build_session_command_reply, resolve_session_command

LeadRecord = Any
NormalizeEvent = Callable[[dict[str, Any]], NormalizedIncomingEvent]
PreprocessEvent = Callable[[NormalizedIncomingEvent], Awaitable[ResilientPreprocessingResult]]


class LeadServiceLike(Protocol):
    """Contrato minimo de persistencia de lead usado pelo pipeline."""

    async def upsert(self, phone: str, session_id: str) -> LeadRecord: ...

    async def update_metadata_by_phone(
        self,
        phone: str,
        *,
        crm_contact_id: str | None = None,
        status: str | None = None,
    ) -> None: ...


class CRMClientLike(Protocol):
    """Contrato minimo de lookup no CRM usado pelo pipeline."""

    async def find_contact_by_phone(self, phone: str) -> Any: ...


class AgentFactoryLike(Protocol):
    """Contrato minimo para construir agente por telefone."""

    def build_for_phone(self, *, contact_phone: str, user_id: str | None = None) -> Any: ...


class SenderClientLike(Protocol):
    """Contrato minimo de envio de mensagem no sender WhatsApp."""

    async def send_text(self, *, phone: str, text: str, session_id: str | None = None) -> Any: ...


class IdempotencyServiceLike(Protocol):
    """Contrato minimo de idempotencia por `event_id`/`message_id`."""

    async def register_or_detect_duplicate(
        self,
        *,
        event_id: str | None,
        message_id: str | None,
        session_id: str,
        contact_phone: str,
    ) -> IdempotencyDecision: ...


@dataclass(frozen=True, slots=True)
class WebhookPipelineResult:
    """Resultado consolidado da execucao do pipeline de webhook."""

    normalized_event: NormalizedIncomingEvent
    event_id: str | None
    idempotency_key: str | None
    is_duplicate: bool
    session_command: SessionCommand | None
    lead_status: str | None
    lead_id: int | None
    crm_contact_id: str | None
    agent_response_text: str
    sent_message_text: str
    sender_status_code: int | None
    sender_payload: dict[str, Any] | None


@dataclass(slots=True)
class WhatsAppWebhookPipelineService:
    """Pipeline E2E: normalizar -> lead upsert -> CRM -> agente -> sender."""

    lead_service: LeadServiceLike
    idempotency_service: IdempotencyServiceLike
    crm_client: CRMClientLike
    agent_factory: AgentFactoryLike
    sender_client: SenderClientLike
    normalize_event: NormalizeEvent = normalize_incoming_event
    preprocess_event: PreprocessEvent = preprocess_event_with_fallback

    async def process(self, raw_payload: dict[str, Any]) -> WebhookPipelineResult:
        """Executa pipeline completo do webhook e retorna metadados da entrega."""
        normalized_event = self.normalize_event(raw_payload)
        event_id = _extract_optional_string(raw_payload.get("eventId"))
        idempotency_decision = await self.idempotency_service.register_or_detect_duplicate(
            event_id=event_id,
            message_id=normalized_event.message_id,
            session_id=normalized_event.session_id,
            contact_phone=normalized_event.contact_phone,
        )
        if idempotency_decision.is_duplicate:
            await self.lead_service.update_metadata_by_phone(
                normalized_event.contact_phone,
                status="duplicate_ignored",
            )
            return WebhookPipelineResult(
                normalized_event=normalized_event,
                event_id=event_id,
                idempotency_key=idempotency_decision.idempotency_key,
                is_duplicate=True,
                session_command=None,
                lead_status="duplicate_ignored",
                lead_id=None,
                crm_contact_id=None,
                agent_response_text="",
                sent_message_text="",
                sender_status_code=None,
                sender_payload=None,
            )

        single_client_session_id = build_single_client_session_id(normalized_event.contact_phone)

        lead = await self.lead_service.upsert(phone=normalized_event.contact_phone, session_id=single_client_session_id)
        lead_id = _extract_optional_int(getattr(lead, "id", None))

        session_command = resolve_session_command(normalized_event.text)
        if session_command is not None:
            command_reply = build_session_command_reply(session_command)
            reset_agent = self.agent_factory.build_for_phone(
                contact_phone=normalized_event.contact_phone,
                user_id=_to_user_id(lead_id),
            )
            await _reset_agent_session(
                agent=reset_agent,
                session_id=single_client_session_id,
                user_id=_to_user_id(lead_id),
            )
            sender_result = await self.sender_client.send_text(
                phone=normalized_event.contact_phone,
                text=command_reply,
                session_id=normalized_event.session_id,
            )
            await self.lead_service.update_metadata_by_phone(
                normalized_event.contact_phone,
                status="session_reset",
            )
            return WebhookPipelineResult(
                normalized_event=normalized_event,
                event_id=event_id,
                idempotency_key=idempotency_decision.idempotency_key,
                is_duplicate=False,
                session_command=session_command,
                lead_status="session_reset",
                lead_id=lead_id,
                crm_contact_id=None,
                agent_response_text="",
                sent_message_text=command_reply,
                sender_status_code=sender_result.status_code,
                sender_payload=sender_result.payload,
            )

        crm_contact = await self.crm_client.find_contact_by_phone(normalized_event.contact_phone)
        crm_contact_id = crm_contact.contact_id if crm_contact is not None else None

        preprocessing_result = await self.preprocess_event(normalized_event)
        agent = self.agent_factory.build_for_phone(
            contact_phone=normalized_event.contact_phone, user_id=_to_user_id(lead_id)
        )
        agent_response_text = await _run_agent(agent=agent, message_for_agent=preprocessing_result.message_for_agent)

        guardrail_result = apply_response_guardrails(agent_response_text)
        sent_message_text = guardrail_result.output_text

        sender_result = await self.sender_client.send_text(
            phone=normalized_event.contact_phone,
            text=sent_message_text,
            session_id=normalized_event.session_id,
        )
        lead_status = "message_sent"
        await self.lead_service.update_metadata_by_phone(
            normalized_event.contact_phone,
            crm_contact_id=crm_contact_id,
            status=lead_status,
        )
        return WebhookPipelineResult(
            normalized_event=normalized_event,
            event_id=event_id,
            idempotency_key=idempotency_decision.idempotency_key,
            is_duplicate=False,
            session_command=None,
            lead_status=lead_status,
            lead_id=lead_id,
            crm_contact_id=crm_contact_id,
            agent_response_text=agent_response_text,
            sent_message_text=sent_message_text,
            sender_status_code=sender_result.status_code,
            sender_payload=sender_result.payload,
        )


def build_whatsapp_webhook_pipeline_service() -> WhatsAppWebhookPipelineService:
    """Constroi service E2E do webhook com dependencias reais de runtime."""
    return WhatsAppWebhookPipelineService(
        lead_service=LeadService(),
        idempotency_service=WebhookIdempotencyService(),
        crm_client=build_crm_client(),
        agent_factory=build_agent_factory(),
        sender_client=build_whatsapp_sender_client(),
    )


async def _run_agent(*, agent: Any, message_for_agent: str) -> str:
    normalized_input = message_for_agent.strip()
    if not normalized_input:
        raise RuntimeError("Mensagem para o agente nao pode ser vazia no pipeline de webhook.")

    if hasattr(agent, "arun"):
        run_output = await agent.arun(normalized_input)
        return _extract_agent_response_text(run_output)

    if hasattr(agent, "run"):
        run_output = agent.run(normalized_input)
        return _extract_agent_response_text(run_output)

    raise RuntimeError("Instancia de agente nao possui metodo `arun`/`run` para execucao do pipeline.")


def _extract_agent_response_text(run_output: Any) -> str:
    if isinstance(run_output, str):
        normalized = run_output.strip()
        if normalized:
            return normalized

    if hasattr(run_output, "get_content_as_string"):
        content = run_output.get_content_as_string()
        if isinstance(content, str) and content.strip():
            return content.strip()

    content_attr = getattr(run_output, "content", None)
    if isinstance(content_attr, str) and content_attr.strip():
        return content_attr.strip()

    if content_attr is not None:
        normalized = str(content_attr).strip()
        if normalized:
            return normalized

    raise RuntimeError("Resposta vazia retornada pelo agente no pipeline de webhook.")


def _extract_optional_int(value: Any) -> int | None:
    if value is None:
        return None

    if isinstance(value, int):
        return value

    normalized = str(value).strip()
    if not normalized:
        return None

    return int(normalized)


def _extract_optional_string(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _to_user_id(lead_id: int | None) -> str | None:
    if lead_id is None:
        return None

    return str(lead_id)


async def _reset_agent_session(*, agent: Any, session_id: str, user_id: str | None) -> None:
    """Executa reset de sessao do agente quando API de sessao estiver disponivel."""
    if hasattr(agent, "adelete_session"):
        try:
            await agent.adelete_session(session_id=session_id, user_id=user_id)
            return
        except Exception:
            return

    if hasattr(agent, "delete_session"):
        try:
            agent.delete_session(session_id=session_id, user_id=user_id)
            return
        except Exception:
            return
