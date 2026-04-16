"""Testes da factory de agente com prompts modulares."""

from pathlib import Path

import pytest
from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.agent.factory import DEFAULT_AGENT_MODEL_ID, AgentFactory, build_agent_factory
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
