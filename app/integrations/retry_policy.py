"""Politicas padrao de retry por tipo de integracao externa."""

from dataclasses import dataclass

CRM_RETRY_STATUS_CODES = (408, 429, 500, 502, 503, 504)
WHATSAPP_SENDER_RETRY_STATUS_CODES = (408, 409, 425, 429, 500, 502, 503, 504)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Representa contrato de retry usado por uma integracao."""

    max_retries: int
    retry_backoff_seconds: float
    retry_status_codes: tuple[int, ...]


def build_crm_retry_policy(*, max_retries: int, retry_backoff_seconds: float) -> RetryPolicy:
    """Retorna politica de retry recomendada para operacoes de CRM."""
    return RetryPolicy(
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
        retry_status_codes=CRM_RETRY_STATUS_CODES,
    )


def build_whatsapp_sender_retry_policy(*, max_retries: int, retry_backoff_seconds: float) -> RetryPolicy:
    """Retorna politica de retry recomendada para sender WhatsApp."""
    return RetryPolicy(
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
        retry_status_codes=WHATSAPP_SENDER_RETRY_STATUS_CODES,
    )
