"""Factory de agente Agno com carregamento modular de prompts."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.models.openai import OpenAIChat

from app.agent.session import build_single_client_session_id
from app.config import Settings, get_settings, load_prompt, settings

DEFAULT_AGENT_MODEL_ID = "gpt-4.1"
PromptLoader = Callable[[Path | None], str]
ModelBuilder = Callable[[Settings], OpenAIChat]


def build_default_openai_model(config: Settings) -> OpenAIChat:
    """Constroi modelo padrao do agente com credenciais do ambiente."""
    return OpenAIChat(id=DEFAULT_AGENT_MODEL_ID, api_key=config.openai_api_key)


@dataclass(slots=True)
class AgentFactory:
    """Monta instancias de agente com prompt composto por modulos."""

    runtime_settings: Settings = field(default_factory=get_settings)
    prompts_dir: Path | None = None
    prompt_loader: PromptLoader = load_prompt
    model_builder: ModelBuilder = build_default_openai_model

    def build(self, *, session_id: str | None = None, user_id: str | None = None) -> Agent:
        """Cria agente Agno pronto para execucao de uma conversa."""
        instructions = self.prompt_loader(self.prompts_dir)
        return Agent(
            name=self.runtime_settings.agent_name,
            model=self.model_builder(self.runtime_settings),
            instructions=instructions,
            session_id=session_id,
            user_id=user_id,
            markdown=False,
        )

    def build_for_phone(self, *, contact_phone: str, user_id: str | None = None) -> Agent:
        """Cria agente com `session_id` derivado de `AGENT_SESSION_PREFIX + telefone`."""
        session_id = build_single_client_session_id(
            contact_phone,
            session_prefix=self.runtime_settings.agent_session_prefix,
        )
        return self.build(session_id=session_id, user_id=user_id)


def build_agent_factory(*, prompts_dir: Path | None = None) -> AgentFactory:
    """Monta AgentFactory com configuracoes globais do ambiente."""
    return AgentFactory(runtime_settings=settings, prompts_dir=prompts_dir)
