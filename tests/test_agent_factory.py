"""Testes da factory de agente com prompts modulares."""

from pathlib import Path

import pytest
from agno.agent import Agent
from agno.models.openai import OpenAIChat, OpenAILike
from agno.models.openrouter import OpenRouter

from app.agent.factory import (
    DEFAULT_AGENT_MODEL_ID,
    DEFAULT_CLAUDE_OPENROUTER_MODEL_ID,
    DEFAULT_GEMINI_MODEL_ID,
    DEFAULT_GROQ_MODEL_ID,
    AgentFactory,
    GEMINI_OPENAI_BASE_URL,
    GROQ_OPENAI_BASE_URL,
    build_agent_factory,
    build_default_agent_model,
)
from app.config import Settings, settings


def test_agent_factory_builds_agent_with_modular_prompt(tmp_path: Path) -> None:
    """Valida criacao de agente com prompt composto e metadados de sessao."""
    (tmp_path / "faq.md").write_text("FAQ", encoding="utf-8")
    (tmp_path / "identity.md").write_text("IDENTITY", encoding="utf-8")
    (tmp_path / "flow_steps.md").write_text("FLOW", encoding="utf-8")

    runtime_settings = Settings(_env_file=None).model_copy(update={"agent_name": "Aurora"})
    factory = AgentFactory(runtime_settings=runtime_settings, prompts_dir=tmp_path)

    agent = factory.build(session_id="spacecont:551199999999", user_id="lead-123")

    assert isinstance(agent, Agent)
    assert agent.name == "Aurora"
    assert agent.instructions == "IDENTITY\n\nFAQ\n\nFLOW"
    assert agent.session_id == "spacecont:551199999999"
    assert agent.user_id == "lead-123"
    assert isinstance(agent.model, OpenAIChat)
    assert agent.model.id == DEFAULT_AGENT_MODEL_ID


def test_agent_factory_raises_when_no_prompt_file_exists(tmp_path: Path) -> None:
    """Garante falha explicita se nao houver prompts para compor instrucoes."""
    factory = AgentFactory(runtime_settings=Settings(_env_file=None), prompts_dir=tmp_path)

    with pytest.raises(RuntimeError) as exc_info:
        factory.build()

    assert "Nenhum arquivo de prompt encontrado" in str(exc_info.value)


def test_build_agent_factory_uses_global_settings_reference(tmp_path: Path) -> None:
    """Confirma que helper usa settings globais e permite sobrescrever prompts_dir."""
    factory = build_agent_factory(prompts_dir=tmp_path)

    assert factory.runtime_settings is settings
    assert factory.prompts_dir == tmp_path


def test_agent_factory_build_for_phone_derives_single_client_session_id(tmp_path: Path) -> None:
    """Valida composicao de `session_id` usando prefixo de ambiente + telefone."""
    (tmp_path / "identity.md").write_text("IDENTITY", encoding="utf-8")
    runtime_settings = Settings(_env_file=None).model_copy(update={"agent_session_prefix": "tenantx"})
    factory = AgentFactory(runtime_settings=runtime_settings, prompts_dir=tmp_path)

    agent = factory.build_for_phone(contact_phone="+55 (11) 97777-0000", user_id="lead-900")

    assert agent.session_id == "tenantx:5511977770000"
    assert agent.user_id == "lead-900"


def test_build_default_agent_model_supports_openrouter_provider() -> None:
    """Constroi modelo OpenRouter com credenciais e id customizados."""
    runtime_settings = Settings(_env_file=None).model_copy(
        update={
            "agent_model_provider": "openrouter",
            "agent_model_id": "anthropic/claude-3.5-sonnet",
            "openrouter_api_key": "or-test-key",
        }
    )

    model = build_default_agent_model(runtime_settings)

    assert isinstance(model, OpenRouter)
    assert model.id == "anthropic/claude-3.5-sonnet"
    assert model.api_key == "or-test-key"


def test_build_default_agent_model_supports_groq_provider() -> None:
    """Constroi modelo Groq usando endpoint OpenAI-compatible."""
    runtime_settings = Settings(_env_file=None).model_copy(
        update={
            "agent_model_provider": "groq",
            "agent_model_id": None,
            "groq_api_key": "groq-test-key",
        }
    )

    model = build_default_agent_model(runtime_settings)

    assert isinstance(model, OpenAILike)
    assert model.id == DEFAULT_GROQ_MODEL_ID
    assert model.base_url == GROQ_OPENAI_BASE_URL
    assert model.api_key == "groq-test-key"


def test_build_default_agent_model_supports_claude_provider_via_openrouter() -> None:
    """Suporta provider Claude com fallback por OpenRouter quando Anthropic nao e usado."""
    runtime_settings = Settings(_env_file=None).model_copy(
        update={
            "agent_model_provider": "claude",
            "agent_model_id": None,
            "openrouter_api_key": "or-claude-key",
            "anthropic_api_key": None,
        }
    )

    model = build_default_agent_model(runtime_settings)

    assert isinstance(model, OpenRouter)
    assert model.id == DEFAULT_CLAUDE_OPENROUTER_MODEL_ID
    assert model.api_key == "or-claude-key"


def test_build_default_agent_model_supports_gemini_provider() -> None:
    """Constroi modelo Gemini via endpoint OpenAI-compatible do Google."""
    runtime_settings = Settings(_env_file=None).model_copy(
        update={
            "agent_model_provider": "gemini",
            "agent_model_id": None,
            "google_api_key": "google-test-key",
        }
    )

    model = build_default_agent_model(runtime_settings)

    assert isinstance(model, OpenAILike)
    assert model.id == DEFAULT_GEMINI_MODEL_ID
    assert model.base_url == GEMINI_OPENAI_BASE_URL
    assert model.api_key == "google-test-key"


def test_build_default_agent_model_supports_chatgpt_provider_alias() -> None:
    """Mantem compatibilidade com alias chatgpt/openai."""
    runtime_settings = Settings(_env_file=None).model_copy(
        update={
            "agent_model_provider": "chatgpt",
            "agent_model_id": "gpt-4.1-mini",
        }
    )

    model = build_default_agent_model(runtime_settings)

    assert isinstance(model, OpenAIChat)
    assert model.id == "gpt-4.1-mini"


def test_build_default_agent_model_raises_for_unknown_provider() -> None:
    """Falha cedo para provider nao suportado."""
    runtime_settings = Settings(_env_file=None).model_copy(update={"agent_model_provider": "cohere"})

    with pytest.raises(RuntimeError) as exc_info:
        build_default_agent_model(runtime_settings)

    assert "Provider de modelo nao suportado" in str(exc_info.value)
