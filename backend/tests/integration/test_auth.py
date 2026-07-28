"""Integration tests for the authentication API surface."""

import pytest

REGISTER_PAYLOAD = {
    "email": "patient1@example.com",
    "password": "Password123",
    "full_name": "Test Patient",
    "role": "patient",
}


@pytest.mark.anyio
async def test_register_creates_user_with_default_role(client) -> None:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    print("\nREGISTER STATUS:", response.status_code)
    print("REGISTER BODY:", response.text)

    assert response.status_code == 201, response.text

    body = response.json()
    assert body["status"] == "success"
    assert body["data"]["email"] == REGISTER_PAYLOAD["email"]
    assert body["data"]["roles"] == ["patient"]
    assert "hashed_password" not in body["data"]


@pytest.mark.anyio
async def test_register_duplicate_email_returns_409(client) -> None:
    first_response = await client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )
    assert first_response.status_code == 201, first_response.text

    response = await client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )

    assert response.status_code == 409, response.text


@pytest.mark.anyio
async def test_register_weak_password_returns_422(client) -> None:
    payload = {
        **REGISTER_PAYLOAD,
        "email": "weak@example.com",
        "password": "short",
    }

    response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 422, response.text


@pytest.mark.anyio
async def test_login_with_valid_credentials_returns_token_pair(client) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )
    assert register_response.status_code == 201, register_response.text

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    print("\nLOGIN STATUS:", response.status_code)
    print("LOGIN BODY:", response.text)

    assert response.status_code == 200, response.text

    body = response.json()["data"]
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_with_invalid_password_returns_401(client) -> None:
    register_response = await client.post(
        "/api/v1/auth/register",
        json=REGISTER_PAYLOAD,
    )
    assert register_response.status_code == 201, register_response.text

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": "WrongPassword1",
        },
    )

    assert response.status_code == 401, response.text


@pytest.mark.anyio
async def test_me_requires_authentication(client) -> None:
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401, response.text


@pytest.mark.anyio
async def test_me_returns_current_user_profile(client) -> None:
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

    access_token = login_response.json()["data"]["access_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["data"]["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.anyio
async def test_refresh_rotates_tokens(client) -> None:
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

    old_refresh_token = login_response.json()["data"]["refresh_token"]

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert refresh_response.status_code == 200, refresh_response.text

    new_tokens = refresh_response.json()["data"]
    assert new_tokens["refresh_token"] != old_refresh_token

    reuse_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": old_refresh_token},
    )

    assert reuse_response.status_code == 401, reuse_response.text


@pytest.mark.anyio
async def test_logout_revokes_refresh_token(client) -> None:
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

    refresh_token = login_response.json()["data"]["refresh_token"]

    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 200, logout_response.text

    refresh_after_logout = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_after_logout.status_code == 401, refresh_after_logout.text