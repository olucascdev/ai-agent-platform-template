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
    assert loaded_settings.migrations_database_url.startswith("postgresql://")
    assert loaded_settings.sqlalchemy_engine_kwargs["pool_pre_ping"] is True
