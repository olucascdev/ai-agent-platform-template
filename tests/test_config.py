"""Testes da configuracao central baseada em variaveis de ambiente."""

import pytest
from pydantic import ValidationError

from app.config import Settings


def test_settings_apply_default_message_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Garante que o delay padrao e aplicado quando a variavel nao e informada."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://ai:ai@localhost:5432/ai")
    monkeypatch.setenv("CRM_BASE_URL", "https://crm.example.com/api/v1")
    monkeypatch.setenv("CRM_TOKEN", "test-crm-token")
    monkeypatch.setenv("WHATSAPP_SENDER_URL", "https://sender.example.com/send/text")
    monkeypatch.setenv("WHATSAPP_TOKEN", "test-whatsapp-token")
    monkeypatch.setenv("AGENT_NAME", "Luna")
    monkeypatch.setenv("AGENT_SESSION_PREFIX", "spacecont")
    monkeypatch.delenv("MESSAGE_DELAY_SECONDS", raising=False)

    loaded_settings = Settings(_env_file=None)

    assert loaded_settings.message_delay_seconds == 3
    assert loaded_settings.http_timeout_seconds == 10.0
    assert loaded_settings.http_max_retries == 2
    assert loaded_settings.http_retry_backoff_seconds == 0.5
    assert loaded_settings.crm_contacts_lookup_path == "/contacts"
    assert loaded_settings.crm_lookup_phone_param == "phone"
    assert loaded_settings.crm_lookup_phone_value_template == "{phone}"
    assert loaded_settings.crm_lookup_service_id_param == "serviceId"
    assert loaded_settings.crm_transfer_path_template == "/contacts/{contact_id}/ticket/transfer"
    assert loaded_settings.crm_auth_header_name == "Authorization"
    assert loaded_settings.crm_auth_header_prefix == "Bearer"
    assert loaded_settings.whatsapp_sender_method == "POST"
    assert loaded_settings.whatsapp_sender_number_field == "number"
    assert loaded_settings.whatsapp_sender_text_field == "text"
    assert loaded_settings.whatsapp_sender_auth_header_name == "Authorization"
    assert loaded_settings.whatsapp_sender_auth_header_prefix == "Bearer"
    assert loaded_settings.audio_transcription_provider == "openai"
    assert loaded_settings.audio_transcription_model == "whisper-1"
    assert loaded_settings.audio_transcription_language is None
    assert loaded_settings.audio_download_timeout_seconds == 20.0
    assert loaded_settings.image_analysis_provider == "google"
    assert loaded_settings.image_analysis_model == "models/gemini-2.0-flash-lite"
    assert loaded_settings.image_analysis_prompt == "Descreva a imagem e extraia o texto visivel de forma organizada."
    assert loaded_settings.image_download_timeout_seconds == 20.0
    assert loaded_settings.pdf_processing_provider == "pypdf"
    assert loaded_settings.pdf_processing_max_pages == 20
    assert loaded_settings.pdf_download_timeout_seconds == 20.0


def test_settings_fail_when_required_value_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Confirma que a validacao falha quando uma chave obrigatoria nao existe."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://ai:ai@localhost:5432/ai")
    monkeypatch.setenv("CRM_BASE_URL", "https://crm.example.com/api/v1")
    monkeypatch.delenv("CRM_TOKEN", raising=False)
    monkeypatch.setenv("WHATSAPP_SENDER_URL", "https://sender.example.com/send/text")
    monkeypatch.setenv("WHATSAPP_TOKEN", "test-whatsapp-token")
    monkeypatch.setenv("AGENT_NAME", "Luna")
    monkeypatch.setenv("AGENT_SESSION_PREFIX", "spacecont")

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "crm_token" in str(exc_info.value).lower()


def test_settings_expose_runtime_and_migration_database_urls(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida URLs derivadas para runtime async e migrations sync."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-google-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@db.abcd.supabase.co:5432/postgres")
    monkeypatch.delenv("DATABASE_URL_MIGRATIONS", raising=False)
    monkeypatch.setenv("CRM_BASE_URL", "https://crm.example.com/api/v1")
    monkeypatch.setenv("CRM_TOKEN", "test-crm-token")
    monkeypatch.setenv("WHATSAPP_SENDER_URL", "https://sender.example.com/send/text")
    monkeypatch.setenv("WHATSAPP_TOKEN", "test-whatsapp-token")
    monkeypatch.setenv("AGENT_NAME", "Luna")
    monkeypatch.setenv("AGENT_SESSION_PREFIX", "spacecont")

    loaded_settings = Settings(_env_file=None)

    assert loaded_settings.runtime_database_url.startswith("postgresql+asyncpg://")
    assert "sslmode=require" in loaded_settings.runtime_database_url
    assert loaded_settings.migrations_database_url.startswith("postgresql+asyncpg://")
    assert loaded_settings.sqlalchemy_engine_kwargs["pool_pre_ping"] is True
