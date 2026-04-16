"""Configuracao central da aplicacao com validacao fail-fast."""

from functools import lru_cache

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


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


# Carregamento imediato para falhar cedo caso alguma variavel obrigatoria esteja ausente.
settings = get_settings()
