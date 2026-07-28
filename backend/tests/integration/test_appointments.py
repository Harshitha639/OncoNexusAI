"""Integration tests for the appointments API."""

from datetime import datetime, timedelta, timezone

import pytest

REGISTER_PAYLOAD = {
    "email": "appointments.patient@example.com",
    "password": "Password123",
    "full_name": "Appointment Patient",
    "role": "patient",
}


async def _authed_headers(client) -> dict[str, str]:
    register_response = await client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )
    assert register_response.status_code == 201, register_response.text

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _future_iso(days: int = 3) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


@pytest.mark.anyio
async def test_book_appointment_succeeds(client) -> None:
    headers = await _authed_headers(client)

    payload = {
        "doctor_name": "Dr. Alice Chen",
        "department": "Oncology",
        "scheduled_at": _future_iso(),
        "reason": "Follow-up consultation",
    }

    response = await client.post(
        "/api/v1/appointments",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201, response.text

    body = response.json()["data"]
    assert body["doctor_name"] == "Dr. Alice Chen"
    assert body["status"] == "scheduled"


@pytest.mark.anyio
async def test_book_appointment_rejects_past_datetime(client) -> None:
    headers = await _authed_headers(client)

    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()

    payload = {
        "doctor_name": "Dr. Past",
        "scheduled_at": past,
    }

    response = await client.post(
        "/api/v1/appointments",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 422, response.text


@pytest.mark.anyio
async def test_list_appointments(client) -> None:
    headers = await _authed_headers(client)

    create_response = await client.post(
        "/api/v1/appointments",
        json={
            "doctor_name": "Dr. Bob",
            "scheduled_at": _future_iso(),
        },
        headers=headers,
    )
    assert create_response.status_code == 201, create_response.text

    response = await client.get(
        "/api/v1/appointments",
        headers=headers,
    )

    assert response.status_code == 200, response.text
    assert len(response.json()["data"]) >= 1


@pytest.mark.anyio
async def test_cancel_appointment(client) -> None:
    headers = await _authed_headers(client)

    book_response = await client.post(
        "/api/v1/appointments",
        json={
            "doctor_name": "Dr. Carter",
            "scheduled_at": _future_iso(),
        },
        headers=headers,
    )
    assert book_response.status_code == 201, book_response.text

    appointment_id = book_response.json()["data"]["id"]

    cancel_response = await client.post(
        f"/api/v1/appointments/{appointment_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code == 200, cancel_response.text
    assert cancel_response.json()["data"]["status"] == "cancelled"

    second_cancel = await client.post(
        f"/api/v1/appointments/{appointment_id}/cancel",
        headers=headers,
    )

    assert second_cancel.status_code == 400, second_cancel.text


@pytest.mark.anyio
async def test_appointments_require_authentication(client) -> None:
    response = await client.get("/api/v1/appointments")

    assert response.status_code == 401, response.text