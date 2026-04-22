"""Testes do carregador de prompts modulares."""

from pathlib import Path

import pytest

from app.config import load_prompt


def test_load_prompt_concatenates_files_in_defined_order(tmp_path: Path) -> None:
    """Valida se a composicao respeita a ordem padrao dos arquivos de prompt."""
    (tmp_path / "faq.md").write_text("FAQ", encoding="utf-8")
    (tmp_path / "identity.md").write_text("IDENTITY", encoding="utf-8")
    (tmp_path / "flow_steps.md").write_text("FLOW", encoding="utf-8")

    prompt = load_prompt(tmp_path)

    assert prompt == "IDENTITY\n\nFAQ\n\nFLOW"


def test_load_prompt_raises_error_when_no_prompt_file_exists(tmp_path: Path) -> None:
    """Confirma erro explicito quando nenhum arquivo de prompt e encontrado."""
    with pytest.raises(RuntimeError) as exc_info:
        load_prompt(tmp_path)

    assert "Nenhum arquivo de prompt encontrado" in str(exc_info.value)


def test_load_prompt_renders_placeholders_from_template_context(tmp_path: Path) -> None:
    """Substitui placeholders `{{var}}` usando contexto informado em runtime."""
    (tmp_path / "identity.md").write_text("Voce e {{agent_name}} da {{business_name}}.", encoding="utf-8")

    prompt = load_prompt(
        tmp_path,
        template_context={
            "agent_name": "Nathalia",
            "business_name": "BM Odontologia",
        },
    )

    assert prompt == "Voce e Nathalia da BM Odontologia."


def test_load_prompt_raises_when_placeholder_value_is_missing(tmp_path: Path) -> None:
    """Falha cedo quando prompt usa placeholder sem valor configurado."""
    (tmp_path / "identity.md").write_text("Agente {{agent_name}}.", encoding="utf-8")

    with pytest.raises(RuntimeError) as exc_info:
        load_prompt(tmp_path)

    assert "placeholder sem valor" in str(exc_info.value)
    assert "agent_name" in str(exc_info.value)


def test_load_prompt_supports_client_profile_overrides(tmp_path: Path) -> None:
    """Usa arquivo de `prompts/clients/<key>` quando existir override por cliente."""
    (tmp_path / "identity.md").write_text("IDENTITY_BASE", encoding="utf-8")
    (tmp_path / "faq.md").write_text("FAQ_BASE", encoding="utf-8")

    client_dir = tmp_path / "clients" / "cliente_a"
    client_dir.mkdir(parents=True)
    (client_dir / "identity.md").write_text("IDENTITY_CLIENTE_A", encoding="utf-8")

    prompt = load_prompt(tmp_path, prompt_client_key="cliente_a")

    assert prompt == "IDENTITY_CLIENTE_A\n\nFAQ_BASE"
