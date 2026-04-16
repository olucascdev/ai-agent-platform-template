"""Testes para garantir pinagem de dependencias do template."""

from pathlib import Path
import tomllib
import unittest


class DependencyPinningTests(unittest.TestCase):
    """Valida se as dependencias principais estao pinadas com versao fixa."""

    def test_runtime_dependencies_are_exactly_pinned(self) -> None:
        """Confere se a lista de runtime segue o contrato da Fase 1/Feature 1.1."""
        pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        project = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))["project"]

        expected_dependencies = [
            "agno==2.5.5",
            "fastapi==0.134.0",
            "uvicorn[standard]==0.41.0",
            "sqlalchemy[asyncio]==2.0.47",
            "asyncpg==0.30.0",
            "httpx==0.28.1",
            "openai==2.24.0",
            "google-generativeai==0.8.5",
            "python-dotenv==1.2.1",
            "alembic==1.16.5",
            "pydantic-settings==2.13.1",
        ]

        self.assertEqual(project["dependencies"], expected_dependencies)


if __name__ == "__main__":
    unittest.main()
