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
