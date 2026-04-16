"""Testes basicos da API principal."""

import unittest

from fastapi.testclient import TestClient

from app.main import app


class MainApiTests(unittest.TestCase):
    """Valida endpoints essenciais do app principal."""

    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_healthcheck_returns_ok_status(self) -> None:
        """Garante que o endpoint de health responde status operacional."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
