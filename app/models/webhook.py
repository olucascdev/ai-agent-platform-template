"""Schemas de entrada e saida para webhook WhatsApp."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel, model_validator


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


class WebhookAttachmentPayload(BaseModel):
    """Representa anexo opcional presente no payload de mensagem."""

    id: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")
    public_url: str | None = Field(default=None, alias="publicUrl")
    name: str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WebhookLastMessagePayload(BaseModel):
    """Representa dados da ultima mensagem recebida no webhook."""

    id: str | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    type: str | None = None
    text: str | None = None
    file: WebhookAttachmentPayload | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WebhookLastMessagesAggregatedPayload(BaseModel):
    """Representa bloco agregado de mensagens e anexos do webhook."""

    text: str | None = None
    files: list[WebhookAttachmentPayload] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WebhookContactPayload(BaseModel):
    """Representa informacoes de contato enviadas pelo webhook."""

    phonenumber: str | None = None
    phone: str | None = None
    number: str | None = None
    name: str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def validate_phone(self) -> "WebhookContactPayload":
        """Garante que ao menos um campo de telefone exista no payload."""
        if _normalize_optional(self.phonenumber) is not None:
            return self
        if _normalize_optional(self.phone) is not None:
            return self
        if _normalize_optional(self.number) is not None:
            return self

        raise ValueError("Campo obrigatorio ausente no payload: contact_phone.")


class WebhookSessionPayload(BaseModel):
    """Representa referencia alternativa de sessao no webhook."""

    id: str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WebhookChannelPayload(BaseModel):
    """Representa metadados do canal de origem do webhook."""

    platform: str | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WhatsAppWebhookEventPayload(BaseModel):
    """Evento canonico aceito pelo endpoint de webhook."""

    session_id: str | None = Field(default=None, alias="sessionId")
    session: WebhookSessionPayload | None = None
    contact: WebhookContactPayload
    last_message: WebhookLastMessagePayload | None = Field(default=None, alias="lastMessage")
    last_messages_aggregated: WebhookLastMessagesAggregatedPayload | None = Field(
        default=None,
        alias="lastMessagesAggregated",
    )
    channel: WebhookChannelPayload | None = None
    event_id: str | None = Field(default=None, alias="eventId")

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    @model_validator(mode="after")
    def validate_session(self) -> "WhatsAppWebhookEventPayload":
        """Garante que `sessionId` exista na raiz ou dentro de `session.id`."""
        if _normalize_optional(self.session_id) is not None:
            return self

        if self.session is not None and _normalize_optional(self.session.id) is not None:
            return self

        raise ValueError("Campo obrigatorio ausente no payload: session_id.")


class WhatsAppWebhookWrappedPayload(BaseModel):
    """Payload com wrapper em `body`, comum em gateways de webhook."""

    body: WhatsAppWebhookEventPayload

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WhatsAppWebhookRequest(RootModel[WhatsAppWebhookEventPayload | WhatsAppWebhookWrappedPayload]):
    """Root schema aceitando payload direto ou encapsulado em `body`."""

    def event_payload(self) -> WhatsAppWebhookEventPayload:
        """Retorna evento normalizado para consumo da rota."""
        if isinstance(self.root, WhatsAppWebhookWrappedPayload):
            return self.root.body

        return self.root


class WhatsAppWebhookAcceptedResponse(BaseModel):
    """Resposta de aceite inicial do endpoint de webhook."""

    status: Literal["accepted"]
    session_id: str
    contact_phone: str
    message_id: str | None = None
    event_id: str | None = None
    is_duplicate: bool = False
    session_command: Literal["reset"] | None = None
