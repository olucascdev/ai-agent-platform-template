"""Factory de agente Agno com carregamento modular de prompts."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from agno.agent import Agent
from agno.models.base import Model
from agno.models.openai import OpenAIChat, OpenAILike
from agno.models.openrouter import OpenRouter

from app.agent.session import build_single_client_session_id
from app.config import Settings, get_settings, load_prompt, settings

DEFAULT_AGENT_MODEL_PROVIDER = "chatgpt"
DEFAULT_AGENT_MODEL_ID = "gpt-4.1"
DEFAULT_OPENROUTER_MODEL_ID = "openai/gpt-4o-mini"
DEFAULT_GROQ_MODEL_ID = "llama-3.3-70b-versatile"
DEFAULT_CLAUDE_MODEL_ID = "claude-3-5-sonnet-20241022"
DEFAULT_CLAUDE_OPENROUTER_MODEL_ID = "anthropic/claude-3.5-sonnet"
DEFAULT_GEMINI_MODEL_ID = "gemini-2.0-flash"

SUPPORTED_AGENT_MODEL_PROVIDERS = ("chatgpt", "openai", "openrouter", "groq", "claude", "gemini")

OPENROUTER_API_BASE_URL = "https://openrouter.ai/api/v1"
GROQ_OPENAI_BASE_URL = "https://api.groq.com/openai/v1"
GEMINI_OPENAI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

PromptLoader = Callable[..., str]
ModelBuilder = Callable[[Settings], Model]


def build_default_openai_model(config: Settings) -> OpenAIChat:
    """Constroi modelo OpenAI/ChatGPT usando chave padrao ou override generico."""
    model_id = _resolve_model_id(provider="chatgpt", configured_model_id=config.agent_model_id)
    api_key = _resolve_api_key(
        config.agent_model_api_key,
        config.openai_api_key,
        error_message="Defina AGENT_MODEL_API_KEY ou OPENAI_API_KEY para usar provider chatgpt/openai.",
    )
    return OpenAIChat(id=model_id, api_key=api_key, base_url=config.agent_model_base_url)


def build_default_agent_model(config: Settings) -> Model:
    """Constroi modelo do agente conforme provider configurado em ambiente."""
    provider = _normalize_provider(config.agent_model_provider)

    if provider in {"chatgpt", "openai"}:
        return build_default_openai_model(config)

    if provider == "openrouter":
        model_id = _resolve_model_id(provider=provider, configured_model_id=config.agent_model_id)
        api_key = _resolve_api_key(
            config.agent_model_api_key,
            config.openrouter_api_key,
            error_message="Defina AGENT_MODEL_API_KEY ou OPENROUTER_API_KEY para usar provider openrouter.",
        )
        return OpenRouter(id=model_id, api_key=api_key, base_url=config.agent_model_base_url or OPENROUTER_API_BASE_URL)

    if provider == "groq":
        model_id = _resolve_model_id(provider=provider, configured_model_id=config.agent_model_id)
        api_key = _resolve_api_key(
            config.agent_model_api_key,
            config.groq_api_key,
            error_message="Defina AGENT_MODEL_API_KEY ou GROQ_API_KEY para usar provider groq.",
        )
        return OpenAILike(id=model_id, api_key=api_key, base_url=config.agent_model_base_url or GROQ_OPENAI_BASE_URL)

    if provider == "claude":
        anthropic_api_key = _normalize_optional(config.anthropic_api_key)
        if anthropic_api_key is not None:
            try:
                from agno.models.anthropic import Claude
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "Provider claude com ANTHROPIC_API_KEY exige pacote `anthropic` instalado. "
                    "Instale a dependencia ou use OPENROUTER_API_KEY para rotear Claude via OpenRouter."
                ) from exc

            model_id = _resolve_model_id(provider=provider, configured_model_id=config.agent_model_id)
            return Claude(id=model_id, api_key=anthropic_api_key)

        model_id = _normalize_optional(config.agent_model_id) or DEFAULT_CLAUDE_OPENROUTER_MODEL_ID
        api_key = _resolve_api_key(
            config.agent_model_api_key,
            config.openrouter_api_key,
            error_message=(
                "Provider claude requer ANTHROPIC_API_KEY (nativo) ou OPENROUTER_API_KEY/AGENT_MODEL_API_KEY "
                "(via OpenRouter)."
            ),
        )
        return OpenRouter(id=model_id, api_key=api_key, base_url=config.agent_model_base_url or OPENROUTER_API_BASE_URL)

    if provider == "gemini":
        model_id = _resolve_model_id(provider=provider, configured_model_id=config.agent_model_id)
        api_key = _resolve_api_key(
            config.agent_model_api_key,
            config.google_api_key,
            error_message="Defina AGENT_MODEL_API_KEY ou GOOGLE_API_KEY para usar provider gemini.",
        )
        return OpenAILike(id=model_id, api_key=api_key, base_url=config.agent_model_base_url or GEMINI_OPENAI_BASE_URL)

    supported = ", ".join(SUPPORTED_AGENT_MODEL_PROVIDERS)
    raise RuntimeError(f"Provider de modelo nao suportado: {provider}. Providers aceitos: {supported}.")


def _normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if not normalized:
        raise RuntimeError("AGENT_MODEL_PROVIDER nao pode ser vazio.")

    return normalized


def _resolve_model_id(*, provider: str, configured_model_id: str | None) -> str:
    normalized_model_id = _normalize_optional(configured_model_id)
    if normalized_model_id is not None:
        return normalized_model_id

    default_model_id_by_provider = {
        "chatgpt": DEFAULT_AGENT_MODEL_ID,
        "openai": DEFAULT_AGENT_MODEL_ID,
        "openrouter": DEFAULT_OPENROUTER_MODEL_ID,
        "groq": DEFAULT_GROQ_MODEL_ID,
        "claude": DEFAULT_CLAUDE_MODEL_ID,
        "gemini": DEFAULT_GEMINI_MODEL_ID,
    }
    if provider not in default_model_id_by_provider:
        supported = ", ".join(SUPPORTED_AGENT_MODEL_PROVIDERS)
        raise RuntimeError(f"Provider de modelo nao suportado: {provider}. Providers aceitos: {supported}.")

    return default_model_id_by_provider[provider]


def _resolve_api_key(*candidates: str | None, error_message: str) -> str:
    for candidate in candidates:
        normalized = _normalize_optional(candidate)
        if normalized is not None:
            return normalized

    raise RuntimeError(error_message)


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


@dataclass(slots=True)
class AgentFactory:
    """Monta instancias de agente com prompt composto por modulos."""

    runtime_settings: Settings = field(default_factory=get_settings)
    prompts_dir: Path | None = None
    prompt_loader: PromptLoader = load_prompt
    model_builder: ModelBuilder = build_default_agent_model

    def build(self, *, session_id: str | None = None, user_id: str | None = None) -> Agent:
        """Cria agente Agno pronto para execucao de uma conversa."""
        try:
            instructions = self.prompt_loader(
                self.prompts_dir,
                prompt_client_key=self.runtime_settings.prompt_client_key,
                template_context=self.runtime_settings.prompt_context,
            )
        except TypeError:
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
