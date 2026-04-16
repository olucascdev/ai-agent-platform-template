"""Configuracao central da aplicacao com validacao fail-fast."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"
PROMPT_FILES_ORDER = (
    "identity.md",
    "departments.md",
    "objections.md",
    "faq.md",
    "flow_steps.md",
)


class Settings(BaseSettings):
    """Agrupa variaveis de ambiente obrigatorias do template."""

    openai_api_key: str = Field(min_length=1)
    google_api_key: str = Field(min_length=1)
    database_url: str = Field(min_length=1)
    crm_base_url: str = Field(min_length=1)
    crm_token: str = Field(min_length=1)
    whatsapp_sender_url: str = Field(min_length=1)
    whatsapp_token: str = Field(min_length=1)
    agent_name: str = Field(min_length=1)
    agent_session_prefix: str = Field(min_length=1)
    message_delay_seconds: int = Field(default=3, ge=0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Carrega e valida as configuracoes na inicializacao da aplicacao."""
    try:
        return Settings()
    except ValidationError as exc:
        invalid_fields = ", ".join(str(error["loc"][0]) for error in exc.errors())
        raise RuntimeError(
            f"Falha ao carregar configuracoes: verifique variaveis obrigatorias no ambiente/.env ({invalid_fields})."
        ) from exc


def load_prompt(prompts_dir: Path | None = None) -> str:
    """Carrega os arquivos de prompt em ordem definida e concatena em uma unica string."""
    resolved_prompts_dir = prompts_dir or PROMPTS_DIR
    prompt_chunks: list[str] = []

    for file_name in PROMPT_FILES_ORDER:
        prompt_file = resolved_prompts_dir / file_name
        if not prompt_file.exists():
            continue

        prompt_chunks.append(prompt_file.read_text(encoding="utf-8").strip())

    if not prompt_chunks:
        raise RuntimeError(
            f"Nenhum arquivo de prompt encontrado em {resolved_prompts_dir}. "
            f"Esperado ao menos um destes arquivos: {', '.join(PROMPT_FILES_ORDER)}."
        )

    return "\n\n".join(prompt_chunks)


# Carregamento imediato para falhar cedo caso alguma variavel obrigatoria esteja ausente.
settings = get_settings()
