"""Testes estruturais do modelo `ProcessedWebhookEvent`."""

from db.models import ProcessedWebhookEvent


def test_processed_webhook_event_table_name() -> None:
    """Garante nome da tabela de idempotencia do webhook."""
    assert ProcessedWebhookEvent.__tablename__ == "processed_webhook_events"


def test_processed_webhook_event_columns_match_phase_contract() -> None:
    """Confere colunas obrigatorias do contrato de idempotencia da fase 7.3."""
    column_names = set(ProcessedWebhookEvent.__table__.columns.keys())

    assert column_names == {
        "id",
        "event_id",
        "message_id",
        "session_id",
        "contact_phone",
        "created_at",
        "updated_at",
    }
    assert ProcessedWebhookEvent.__table__.columns["session_id"].nullable is False
    assert ProcessedWebhookEvent.__table__.columns["contact_phone"].nullable is False
