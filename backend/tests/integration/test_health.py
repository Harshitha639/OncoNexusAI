"""Integration tests for the health check endpoints."""

import pytest


@pytest.mark.anyio
async def test_health_check(client) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "service" in body["data"]
