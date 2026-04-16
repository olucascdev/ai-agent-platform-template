"""Testes assincronos do endpoint de health da API."""

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_healthcheck_returns_ok_in_async_client() -> None:
    """Garante que o endpoint de health responde corretamente em fluxo async."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
