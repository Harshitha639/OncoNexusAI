"""Integration tests for the Phase 4 guidance endpoints (Personalized Guidance
and Caregiver Support). Both agents require a completed AI summary, which in
turn requires completed OCR — neither can be produced deterministically in
this test environment without a live Gemini call, so these tests focus on
the precondition/authorization guardrails, mirroring `test_summary_requires_
completed_ocr` in `test_reports.py`.
"""

import io

import pytest

REGISTER_PAYLOAD = {
    "email": "guidance.patient@onconexus.test",
    "password": "Password123",
    "full_name": "Guidance Patient",
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


async def _upload_report(client, headers) -> str:
    files = {"file": ("report.pdf", io.BytesIO(b"%PDF-1.4\nfake\n%%EOF"), "application/pdf")}
    response = await client.post(
        "/api/v1/reports", data={"title": "Guidance Test Report"}, files=files, headers=headers
    )
    return response.json()["data"]["id"]


@pytest.mark.anyio
async def test_patient_guidance_requires_authentication(client) -> None:
    response = await client.post("/api/v1/reports/00000000-0000-0000-0000-000000000000/guidance/patient")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_caregiver_guidance_requires_authentication(client) -> None:
    response = await client.post(
        "/api/v1/reports/00000000-0000-0000-0000-000000000000/guidance/caregiver"
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_patient_guidance_404_for_unknown_report(client) -> None:
    headers = await _authed_headers(client)
    response = await client.post(
        "/api/v1/reports/00000000-0000-0000-0000-000000000000/guidance/patient",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_patient_guidance_blocked_until_ocr_completes(client) -> None:
    headers = await _authed_headers(client)
    report_id = await _upload_report(client, headers)

    response = await client.post(f"/api/v1/reports/{report_id}/guidance/patient", headers=headers)
    # OCR runs in the background and is not guaranteed to have completed;
    # either way, generation must never silently succeed without a
    # completed analysis, so 400 (OCR pending) or 409 (analysis missing)
    # are the only acceptable outcomes.
    assert response.status_code in (400, 409)


@pytest.mark.anyio
async def test_caregiver_guidance_blocked_until_ocr_completes(client) -> None:
    headers = await _authed_headers(client)
    report_id = await _upload_report(client, headers)

    response = await client.post(f"/api/v1/reports/{report_id}/guidance/caregiver", headers=headers)
    assert response.status_code in (400, 409)


@pytest.mark.anyio
async def test_get_patient_guidance_404_before_generation(client) -> None:
    headers = await _authed_headers(client)
    report_id = await _upload_report(client, headers)

    response = await client.get(f"/api/v1/reports/{report_id}/guidance/patient", headers=headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_caregiver_guidance_404_before_generation(client) -> None:
    headers = await _authed_headers(client)
    report_id = await _upload_report(client, headers)

    response = await client.get(f"/api/v1/reports/{report_id}/guidance/caregiver", headers=headers)
    assert response.status_code == 404


@pytest.mark.anyio
async def test_cannot_generate_guidance_for_another_patients_report(client) -> None:
    headers_a = await _authed_headers(client)
    report_id = await _upload_report(client, headers_a)

    other_payload = {
        "email": "other.guidance.patient@onconexus.test",
        "password": "Password123",
        "full_name": "Other Guidance Patient",
        "role": "patient",
    }
    await client.post("/api/v1/auth/register", json=other_payload)
    login_b = await client.post(
        "/api/v1/auth/login",
        json={"email": other_payload["email"], "password": other_payload["password"]},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['data']['access_token']}"}

    response = await client.post(f"/api/v1/reports/{report_id}/guidance/patient", headers=headers_b)
    assert response.status_code == 404
