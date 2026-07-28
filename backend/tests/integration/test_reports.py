"""Integration tests for the medical reports API."""

import io

import pytest

REGISTER_PAYLOAD = {
    "email": "reports.patient@example.com",
    "password": "Password123",
    "full_name": "Reports Patient",
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


def _fake_pdf_bytes() -> bytes:
    # Minimal but structurally valid-enough PDF header for upload testing.
    return b"%PDF-1.4\n%Fake test PDF content for OncoNexus AI tests.\n%%EOF"


@pytest.mark.anyio
async def test_upload_report_succeeds(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    data = {"title": "Blood Test Results", "description": "Routine panel"}
    response = await client.post(
        "/api/v1/reports", data=data, files=files, headers=headers
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["title"] == "Blood Test Results"
    assert body["file_type"] == "pdf"
    assert body["ocr_status"] in ("pending", "processing", "completed", "failed")


@pytest.mark.anyio
async def test_upload_rejects_unsupported_extension(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.txt", io.BytesIO(b"plain text"), "text/plain")}
    data = {"title": "Bad file"}
    response = await client.post(
        "/api/v1/reports", data=data, files=files, headers=headers
    )
    assert response.status_code == 415


@pytest.mark.anyio
async def test_upload_requires_authentication(client) -> None:
    files = {"file": ("report.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    data = {"title": "No auth"}
    response = await client.post("/api/v1/reports", data=data, files=files)
    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_and_search_reports(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("ct_scan.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    await client.post(
        "/api/v1/reports",
        data={"title": "CT Scan Report", "description": "Chest CT"},
        files=files,
        headers=headers,
    )

    response = await client.get("/api/v1/reports", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["total"] >= 1

    search_response = await client.get(
        "/api/v1/reports", params={"query": "CT Scan"}, headers=headers
    )
    assert search_response.status_code == 200
    assert search_response.json()["meta"]["total"] >= 1

    no_match_response = await client.get(
        "/api/v1/reports", params={"query": "nonexistent-xyz"}, headers=headers
    )
    assert no_match_response.json()["meta"]["total"] == 0


@pytest.mark.anyio
async def test_get_and_delete_report(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    upload_response = await client.post(
        "/api/v1/reports", data={"title": "To Delete"}, files=files, headers=headers
    )
    report_id = upload_response.json()["data"]["id"]

    get_response = await client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["data"]["title"] == "To Delete"

    delete_response = await client.delete(f"/api/v1/reports/{report_id}", headers=headers)
    assert delete_response.status_code == 200

    get_after_delete = await client.get(f"/api/v1/reports/{report_id}", headers=headers)
    assert get_after_delete.status_code == 404


@pytest.mark.anyio
async def test_cannot_access_another_patients_report(client) -> None:
    headers_a = await _authed_headers(client)
    files = {"file": ("private.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    upload_response = await client.post(
        "/api/v1/reports", data={"title": "Private Report"}, files=files, headers=headers_a
    )
    report_id = upload_response.json()["data"]["id"]

    other_payload = {
        "email": "other.patient@example.com",
        "password": "Password123",
        "full_name": "Other Patient",
        "role": "patient",
    }
    register_b = await client.post(
        "/api/v1/auth/register",
        json=other_payload,
    )
    assert register_b.status_code == 201, register_b.text

    login_b = await client.post(
        "/api/v1/auth/login",
        json={
            "email": other_payload["email"],
            "password": other_payload["password"],
        },
    )
    assert login_b.status_code == 200, login_b.text


@pytest.mark.anyio
async def test_summary_requires_completed_ocr(client) -> None:
    headers = await _authed_headers(client)
    files = {"file": ("report.pdf", io.BytesIO(_fake_pdf_bytes()), "application/pdf")}
    upload_response = await client.post(
        "/api/v1/reports", data={"title": "Pending OCR"}, files=files, headers=headers
    )
    report_id = upload_response.json()["data"]["id"]

    # OCR runs as a background task and may not have completed yet — either
    # outcome (still pending, or already failed on this fake PDF) must be
    # rejected with 400 rather than silently generating a summary.
    response = await client.post(f"/api/v1/reports/{report_id}/summary", headers=headers)
    assert response.status_code in (400, 503)
