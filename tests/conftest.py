"""Configuracoes de teste compartilhadas para a suite."""

import os


def _set_required_test_environment() -> None:
    """Define valores padrao para variaveis obrigatorias durante os testes."""
    required_env = {
        "OPENAI_API_KEY": "test-openai-key",
        "GOOGLE_API_KEY": "test-google-key",
        "DATABASE_URL": "postgresql+asyncpg://ai:ai@localhost:5432/ai",
        "CRM_BASE_URL": "https://crm.example.com/api/v1",
        "CRM_TOKEN": "test-crm-token",
        "WHATSAPP_SENDER_URL": "https://sender.example.com/send/text",
        "WHATSAPP_TOKEN": "test-whatsapp-token",
        "AGENT_NAME": "Luna",
        "AGENT_SESSION_PREFIX": "spacecont",
    }

    for key, value in required_env.items():
        os.environ.setdefault(key, value)


_set_required_test_environment()
