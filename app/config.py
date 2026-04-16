"""Configuracao central da aplicacao com validacao fail-fast."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from db.url import (
    build_sqlalchemy_engine_kwargs,
    resolve_migrations_database_url,
    resolve_runtime_database_url,
)

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
    database_url_migrations: str | None = None
    crm_base_url: str = Field(min_length=1)
    crm_token: str = Field(min_length=1)
    crm_contacts_lookup_path: str = Field(default="/contacts", min_length=1)
    crm_lookup_phone_param: str = Field(default="phone", min_length=1)
    crm_lookup_phone_value_template: str = Field(default="{phone}", min_length=1)
    crm_lookup_service_id_param: str = Field(default="serviceId", min_length=1)
    crm_service_id: str | None = None
    crm_transfer_path_template: str = Field(default="/contacts/{contact_id}/ticket/transfer", min_length=1)
    crm_auth_header_name: str = Field(default="Authorization", min_length=1)
    crm_auth_header_prefix: str = Field(default="Bearer")
    whatsapp_sender_url: str = Field(min_length=1)
    whatsapp_token: str = Field(min_length=1)
    whatsapp_sender_method: str = Field(default="POST", min_length=1)
    whatsapp_sender_number_field: str = Field(default="number", min_length=1)
    whatsapp_sender_text_field: str = Field(default="text", min_length=1)
    whatsapp_sender_auth_header_name: str = Field(default="Authorization", min_length=1)
    whatsapp_sender_auth_header_prefix: str = Field(default="Bearer")
    agent_name: str = Field(min_length=1)
    agent_session_prefix: str = Field(min_length=1)
    agent_model_provider: str = Field(default="chatgpt", min_length=1)
    agent_model_id: str | None = None
    agent_model_api_key: str | None = None
    agent_model_base_url: str | None = None
    openrouter_api_key: str | None = None
    groq_api_key: str | None = None
    anthropic_api_key: str | None = None
    message_delay_seconds: int = Field(default=3, ge=0)
    http_timeout_seconds: float = Field(default=10.0, gt=0)
    http_max_retries: int = Field(default=2, ge=0)
    http_retry_backoff_seconds: float = Field(default=0.5, ge=0)
    audio_transcription_provider: str = Field(default="openai", min_length=1)
    audio_transcription_model: str = Field(default="whisper-1", min_length=1)
    audio_transcription_language: str | None = None
    audio_download_timeout_seconds: float = Field(default=20.0, gt=0)
    image_analysis_provider: str = Field(default="google", min_length=1)
    image_analysis_model: str = Field(default="models/gemini-2.0-flash-lite", min_length=1)
    image_analysis_prompt: str = Field(default="Descreva a imagem e extraia o texto visivel de forma organizada.")
    image_download_timeout_seconds: float = Field(default=20.0, gt=0)
    pdf_processing_provider: str = Field(default="pypdf", min_length=1)
    pdf_processing_max_pages: int = Field(default=20, ge=1)
    pdf_download_timeout_seconds: float = Field(default=20.0, gt=0)
    media_failure_fallback_text: str = Field(
        default="Nao foi possivel processar completamente a midia enviada. Oriente o usuario a reenviar o conteudo em texto ou em formato suportado.",
        min_length=1,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def runtime_database_url(self) -> str:
        """Retorna URL de runtime normalizada para engine async."""
        return resolve_runtime_database_url(self.database_url)

    @property
    def migrations_database_url(self) -> str:
        """Retorna URL sync para Alembic, com fallback para `DATABASE_URL`."""
        return resolve_migrations_database_url(self.database_url, self.database_url_migrations)

    @property
    def sqlalchemy_engine_kwargs(self) -> dict[str, object]:
        """Retorna configuracoes padrao de engine para conexoes mais estaveis."""
        return build_sqlalchemy_engine_kwargs(self.runtime_database_url)


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
