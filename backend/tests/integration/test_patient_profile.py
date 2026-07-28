"""Integration tests for the patient profile API."""

import pytest

REGISTER_PAYLOAD = {
    "email": "profile.patient@example.com",
    "password": "Password123",
    "full_name": "Profile Patient",
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


@pytest.mark.anyio
async def test_get_profile_before_creation_returns_404(client) -> None:
    headers = await _authed_headers(client)
    response = await client.get("/api/v1/patients/me/profile", headers=headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_profile_succeeds(client) -> None:
    headers = await _authed_headers(client)
    payload = {
        "date_of_birth": "1990-05-10",
        "gender": "female",
        "phone_number": "+1-555-0100",
        "blood_group": "O+",
        "height_cm": 165.5,
        "weight_kg": 60.2,
        "smoking_status": "never",
        "alcohol_consumption": "occasional",
    }
    response = await client.post(
        "/api/v1/patients/me/profile", json=payload, headers=headers
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["gender"] == "female"
    assert body["completion_percentage"] > 0


@pytest.mark.anyio
async def test_create_profile_twice_returns_409(client) -> None:
    headers = await _authed_headers(client)
    payload = {"gender": "male"}
    await client.post("/api/v1/patients/me/profile", json=payload, headers=headers)
    response = await client.post("/api/v1/patients/me/profile", json=payload, headers=headers)
    assert response.status_code == 409


@pytest.mark.anyio
async def test_update_profile_succeeds(client) -> None:
    headers = await _authed_headers(client)
    await client.post(
        "/api/v1/patients/me/profile", json={"gender": "male"}, headers=headers
    )
    response = await client.put(
        "/api/v1/patients/me/profile",
        json={"phone_number": "+1-555-0199", "smoking_status": "former"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["phone_number"] == "+1-555-0199"
    assert body["smoking_status"] == "former"
    assert body["gender"] == "male"  # untouched fields are preserved


@pytest.mark.anyio
async def test_profile_requires_authentication(client) -> None:
    response = await client.get("/api/v1/patients/me/profile")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_future_date_of_birth_rejected(client) -> None:
    headers = await _authed_headers(client)
    response = await client.post(
        "/api/v1/patients/me/profile",
        json={"date_of_birth": "2999-01-01"},
        headers=headers,
    )
    assert response.status_code == 422
