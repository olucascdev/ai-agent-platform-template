"""Testes das politicas de retry por integracao da fase 4.4."""

from app.integrations.retry_policy import (
    CRM_RETRY_STATUS_CODES,
    WHATSAPP_SENDER_RETRY_STATUS_CODES,
    build_crm_retry_policy,
    build_whatsapp_sender_retry_policy,
)


def test_build_crm_retry_policy_uses_crm_status_contract() -> None:
    """Valida contrato de status retryavel para integracoes CRM."""
    policy = build_crm_retry_policy(max_retries=3, retry_backoff_seconds=0.75)

    assert policy.max_retries == 3
    assert policy.retry_backoff_seconds == 0.75
    assert policy.retry_status_codes == CRM_RETRY_STATUS_CODES
    assert 408 in policy.retry_status_codes


def test_build_sender_retry_policy_uses_sender_status_contract() -> None:
    """Valida contrato de status retryavel para sender WhatsApp."""
    policy = build_whatsapp_sender_retry_policy(max_retries=4, retry_backoff_seconds=0.25)

    assert policy.max_retries == 4
    assert policy.retry_backoff_seconds == 0.25
    assert policy.retry_status_codes == WHATSAPP_SENDER_RETRY_STATUS_CODES
    assert 425 in policy.retry_status_codes
