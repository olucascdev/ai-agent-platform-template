"""Testes da estrutura minima do arquivo .env.example."""

from pathlib import Path
import unittest


class EnvExampleTemplateTests(unittest.TestCase):
    """Valida se as variaveis obrigatorias do template estao documentadas."""

    def test_env_example_contains_required_keys(self) -> None:
        """Garante que o arquivo de exemplo contenha todas as chaves obrigatorias."""
        env_example_path = Path(__file__).resolve().parents[1] / ".env.example"
        content = env_example_path.read_text(encoding="utf-8")

        required_keys = {
            "OPENAI_API_KEY",
            "GOOGLE_API_KEY",
            "DATABASE_URL",
            "CRM_BASE_URL",
            "CRM_TOKEN",
            "WHATSAPP_SENDER_URL",
            "WHATSAPP_TOKEN",
            "AGENT_NAME",
            "AGENT_SESSION_PREFIX",
            "MESSAGE_DELAY_SECONDS",
        }

        parsed_keys = {
            line.split("=", maxsplit=1)[0].strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#") and "=" in line
        }

        self.assertEqual(parsed_keys, required_keys)

    def test_env_example_uses_default_message_delay(self) -> None:
        """Confere se o delay padrao de mensagens foi definido como 3 segundos."""
        env_example_path = Path(__file__).resolve().parents[1] / ".env.example"
        content = env_example_path.read_text(encoding="utf-8")

        self.assertIn("MESSAGE_DELAY_SECONDS=3", content)


if __name__ == "__main__":
    unittest.main()
