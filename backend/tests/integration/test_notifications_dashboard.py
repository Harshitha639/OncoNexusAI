"""Integration tests for the notifications and dashboard APIs."""

import io

import pytest

REGISTER_PAYLOAD = {
    "email": "notifications.patient@onconexus.test",
    "password": "Password123",
    "full_name": "Notifications Patient",
    "role": "patient",
}


async def _authed_headers(client) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_report_upload_creates_notification(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.pdf", io.BytesIO(b"%PDF-1.4\nfake\n%%EOF"), "application/pdf")}
    await client.post(
        "/api/v1/reports", data={"title": "Notif Test"}, files=files, headers=headers
    )

    response = await client.get("/api/v1/notifications", headers=headers)
    assert response.status_code == 200
    notifications = response.json()["data"]
    assert any(n["type"] == "report_upload_success" for n in notifications)


@pytest.mark.anyio
async def test_unread_count_and_mark_as_read(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.pdf", io.BytesIO(b"%PDF-1.4\nfake\n%%EOF"), "application/pdf")}
    await client.post(
        "/api/v1/reports", data={"title": "Unread Test"}, files=files, headers=headers
    )

    count_response = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert count_response.status_code == 200
    assert count_response.json()["data"]["unread_count"] >= 1

    notifications = (await client.get("/api/v1/notifications", headers=headers)).json()["data"]
    notification_id = notifications[0]["id"]

    read_response = await client.post(
        f"/api/v1/notifications/{notification_id}/read", headers=headers
    )
    assert read_response.status_code == 200
    assert read_response.json()["data"]["is_read"] is True


@pytest.mark.anyio
async def test_notifications_require_authentication(client) -> None:
    response = await client.get("/api/v1/notifications")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_dashboard_returns_summary(client) -> None:
    headers = await _authed_headers(client)
    response = await client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["welcome"]["email"] == REGISTER_PAYLOAD["email"]
    assert "profile_completion_percentage" in body
    assert isinstance(body["recent_reports"], list)
    assert isinstance(body["upcoming_appointments"], list)


@pytest.mark.anyio
async def test_dashboard_requires_authentication(client) -> None:
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 401
