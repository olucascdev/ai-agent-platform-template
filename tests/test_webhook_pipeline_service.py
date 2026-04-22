"""Testes do pipeline E2E do webhook (fase 7.2)."""

from types import SimpleNamespace
from typing import Any

from app.agent.guardrails import DEFAULT_GUARDRAIL_FALLBACK_TEXT
from app.core.webhook_idempotency_service import IdempotencyDecision
from app.preprocessing import ResilientPreprocessingResult, normalize_incoming_event
from app.services.webhook_pipeline import WhatsAppWebhookPipelineService


class _FakeLeadService:
    """Service fake para capturar chamadas de upsert de lead."""

    def __init__(self, order: list[str]) -> None:
        self.order = order
        self.last_call: tuple[str, str] | None = None
        self.metadata_updates: list[tuple[str, str | None, str | None]] = []

    async def upsert(self, phone: str, session_id: str) -> Any:
        self.order.append("lead_upsert")
        self.last_call = (phone, session_id)
        return SimpleNamespace(id=42)

    async def update_metadata_by_phone(
        self,
        phone: str,
        *,
        crm_contact_id: str | None = None,
        status: str | None = None,
    ) -> None:
        self.order.append("lead_update_metadata")
        self.metadata_updates.append((phone, crm_contact_id, status))


class _FakeIdempotencyService:
    """Servico fake para controlar decisao de duplicidade no pipeline."""

    def __init__(self, order: list[str], *, is_duplicate: bool = False) -> None:
        self.order = order
        self.is_duplicate = is_duplicate
        self.last_call: tuple[str | None, str | None, str, str] | None = None

    async def register_or_detect_duplicate(
        self,
        *,
        event_id: str | None,
        message_id: str | None,
        session_id: str,
        contact_phone: str,
    ) -> IdempotencyDecision:
        self.order.append("idempotency")
        self.last_call = (event_id, message_id, session_id, contact_phone)
        if self.is_duplicate:
            return IdempotencyDecision(is_duplicate=True, idempotency_key="event:evt-101")

        return IdempotencyDecision(is_duplicate=False, idempotency_key="event:evt-101")


class _FakeCRMClient:
    """Cliente CRM fake para validar etapa de lookup."""

    def __init__(self, order: list[str], contact_id: str | None = "crm-42") -> None:
        self.order = order
        self.contact_id = contact_id
        self.last_phone: str | None = None

    async def find_contact_by_phone(self, phone: str) -> Any:
        self.order.append("crm_lookup")
        self.last_phone = phone
        if self.contact_id is None:
            return None

        return SimpleNamespace(contact_id=self.contact_id)


class _FakeAgent:
    """Agente fake para controlar texto retornado no pipeline."""

    def __init__(self, order: list[str], response_text: str) -> None:
        self.order = order
        self.response_text = response_text
        self.last_prompt: str | None = None
        self.deleted_session: tuple[str, str | None] | None = None

    async def arun(self, prompt: str) -> Any:
        self.order.append("agent_run")
        self.last_prompt = prompt
        return SimpleNamespace(content=self.response_text)

    async def adelete_session(self, session_id: str, user_id: str | None = None) -> None:
        self.order.append("agent_delete_session")
        self.deleted_session = (session_id, user_id)


class _FakeAgentFactory:
    """Factory fake para validar construcao do agente por telefone."""

    def __init__(self, order: list[str], agent: _FakeAgent) -> None:
        self.order = order
        self.agent = agent
        self.last_call: tuple[str, str | None] | None = None

    def build_for_phone(self, *, contact_phone: str, user_id: str | None = None) -> _FakeAgent:
        self.order.append("agent_build")
        self.last_call = (contact_phone, user_id)
        return self.agent


class _FakeSenderClient:
    """Sender fake para validar ultima etapa do pipeline."""

    def __init__(self, order: list[str]) -> None:
        self.order = order
        self.last_payload: tuple[str, str, str | None] | None = None

    async def send_text(self, *, phone: str, text: str, session_id: str | None = None) -> Any:
        self.order.append("sender_send")
        self.last_payload = (phone, text, session_id)
        return SimpleNamespace(status_code=200, payload={"queued": True})


async def _fake_preprocess_event(event: Any, order: list[str]) -> ResilientPreprocessingResult:
    order.append("preprocess")
    return ResilientPreprocessingResult(
        event=event,
        composed_input=None,
        message_for_agent="[mensagem_principal]\nfonte=text\nQuero ajuda",
        used_fallback_message=False,
        audio_transcription=None,
        image_analysis=None,
        pdf_processing=None,
        issues=(),
    )


def _build_payload() -> dict[str, Any]:
    return {
        "eventId": "evt-101",
        "sessionId": "sessao-original",
        "contact": {"phonenumber": "+5511999999999", "name": "Joel"},
        "lastMessage": {"id": "msg-101", "type": "TEXT", "text": "Quero ajuda"},
    }


async def test_webhook_pipeline_runs_expected_sequence_end_to_end() -> None:
    """Valida ordem das etapas: normalizar -> lead -> CRM -> agente -> sender."""
    order: list[str] = []
    lead_service = _FakeLeadService(order)
    idempotency_service = _FakeIdempotencyService(order)
    crm_client = _FakeCRMClient(order)
    agent = _FakeAgent(order, response_text="Resposta final do agente")
    agent_factory = _FakeAgentFactory(order, agent=agent)
    sender_client = _FakeSenderClient(order)

    def normalize_with_tracking(raw_payload: dict[str, Any]) -> Any:
        order.append("normalize")
        return normalize_incoming_event(raw_payload)

    async def preprocess_with_tracking(event: Any) -> ResilientPreprocessingResult:
        return await _fake_preprocess_event(event, order)

    service = WhatsAppWebhookPipelineService(
        lead_service=lead_service,
        idempotency_service=idempotency_service,
        crm_client=crm_client,
        agent_factory=agent_factory,
        sender_client=sender_client,
        normalize_event=normalize_with_tracking,
        preprocess_event=preprocess_with_tracking,
    )

    result = await service.process(_build_payload())

    assert order == [
        "normalize",
        "idempotency",
        "lead_upsert",
        "crm_lookup",
        "preprocess",
        "agent_build",
        "agent_run",
        "sender_send",
        "lead_update_metadata",
    ]
    assert lead_service.last_call == ("+5511999999999", "spacecont:5511999999999")
    assert idempotency_service.last_call == ("evt-101", "msg-101", "sessao-original", "+5511999999999")
    assert crm_client.last_phone == "+5511999999999"
    assert agent_factory.last_call == ("+5511999999999", "42")
    assert sender_client.last_payload == ("+5511999999999", "Resposta final do agente", "sessao-original")
    assert lead_service.metadata_updates == [
        ("+5511999999999", "crm-42", "message_sent"),
    ]

    assert result.event_id == "evt-101"
    assert result.idempotency_key == "event:evt-101"
    assert result.is_duplicate is False
    assert result.session_command is None
    assert result.lead_status == "message_sent"
    assert result.lead_id == 42
    assert result.crm_contact_id == "crm-42"
    assert result.sender_status_code == 200
    assert result.sender_payload == {"queued": True}


async def test_webhook_pipeline_applies_guardrail_fallback_before_sender() -> None:
    """Garante bloqueio de conteudo proibido antes de enviar mensagem ao sender."""
    order: list[str] = []
    lead_service = _FakeLeadService(order)
    idempotency_service = _FakeIdempotencyService(order)
    crm_client = _FakeCRMClient(order, contact_id=None)
    agent = _FakeAgent(order, response_text="Use o token sk-ABCD1234ABCD1234ABCD")
    agent_factory = _FakeAgentFactory(order, agent=agent)
    sender_client = _FakeSenderClient(order)

    service = WhatsAppWebhookPipelineService(
        lead_service=lead_service,
        idempotency_service=idempotency_service,
        crm_client=crm_client,
        agent_factory=agent_factory,
        sender_client=sender_client,
        normalize_event=normalize_incoming_event,
        preprocess_event=lambda event: _fake_preprocess_event(event, order),
    )

    result = await service.process(_build_payload())

    assert result.crm_contact_id is None
    assert result.is_duplicate is False
    assert result.session_command is None
    assert result.lead_status == "message_sent"
    assert result.sent_message_text == DEFAULT_GUARDRAIL_FALLBACK_TEXT
    assert sender_client.last_payload == ("+5511999999999", DEFAULT_GUARDRAIL_FALLBACK_TEXT, "sessao-original")
    assert lead_service.metadata_updates == [
        ("+5511999999999", None, "message_sent"),
    ]


async def test_webhook_pipeline_short_circuits_when_event_is_duplicate() -> None:
    """Garante que duplicados nao disparam efeitos colaterais no pipeline."""
    order: list[str] = []
    lead_service = _FakeLeadService(order)
    idempotency_service = _FakeIdempotencyService(order, is_duplicate=True)
    crm_client = _FakeCRMClient(order)
    agent = _FakeAgent(order, response_text="Nao deve executar")
    agent_factory = _FakeAgentFactory(order, agent=agent)
    sender_client = _FakeSenderClient(order)

    service = WhatsAppWebhookPipelineService(
        lead_service=lead_service,
        idempotency_service=idempotency_service,
        crm_client=crm_client,
        agent_factory=agent_factory,
        sender_client=sender_client,
        normalize_event=normalize_incoming_event,
        preprocess_event=lambda event: _fake_preprocess_event(event, order),
    )

    result = await service.process(_build_payload())

    assert order == ["idempotency", "lead_update_metadata"]
    assert result.is_duplicate is True
    assert result.idempotency_key == "event:evt-101"
    assert result.lead_status == "duplicate_ignored"
    assert result.lead_id is None
    assert result.session_command is None
    assert result.crm_contact_id is None
    assert result.sender_status_code is None
    assert result.sender_payload is None
    assert lead_service.metadata_updates == [
        ("+5511999999999", None, "duplicate_ignored"),
    ]


async def test_webhook_pipeline_handles_reset_command_before_crm_and_agent_reply() -> None:
    """Comando `reset` deve limpar sessao e enviar confirmacao sem rodar CRM/preprocess/LLM."""
    order: list[str] = []
    lead_service = _FakeLeadService(order)
    idempotency_service = _FakeIdempotencyService(order)
    crm_client = _FakeCRMClient(order)
    agent = _FakeAgent(order, response_text="Nao deve responder")
    agent_factory = _FakeAgentFactory(order, agent=agent)
    sender_client = _FakeSenderClient(order)

    service = WhatsAppWebhookPipelineService(
        lead_service=lead_service,
        idempotency_service=idempotency_service,
        crm_client=crm_client,
        agent_factory=agent_factory,
        sender_client=sender_client,
        normalize_event=normalize_incoming_event,
        preprocess_event=lambda event: _fake_preprocess_event(event, order),
    )

    payload = _build_payload()
    payload["lastMessage"]["text"] = "/reset"
    result = await service.process(payload)

    assert order == [
        "idempotency",
        "lead_upsert",
        "agent_build",
        "agent_delete_session",
        "sender_send",
        "lead_update_metadata",
    ]
    assert result.session_command == "reset"
    assert result.lead_status == "session_reset"
    assert result.crm_contact_id is None
    assert result.agent_response_text == ""
    assert "Sessao reiniciada" in result.sent_message_text
    assert agent.deleted_session == ("spacecont:5511999999999", "42")
    assert lead_service.metadata_updates == [
        ("+5511999999999", None, "session_reset"),
    ]
