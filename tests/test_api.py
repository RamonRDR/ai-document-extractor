"""Functional end-to-end API assertions with zero paid AI calls."""

from fastapi.testclient import TestClient


def _upload(client: TestClient, png: bytes) -> dict:
    res = client.post("/api/v1/extract", files={"file": ("synthetic.png", png, "image/png")})
    assert res.status_code == 200
    return res.json()


def test_health_and_openapi(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 200
    assert client.get("/").status_code == 200


def test_demo_and_review(client: TestClient, png: bytes) -> None:
    extracted = _upload(client, png)
    assert extracted["mode"] == "demo"
    assert "No AI extraction" in extracted["notice"]
    corrected = dict(extracted["document"])
    corrected["total"] = "12.50"
    corrected["subtotal"] = "12.50"
    corrected["items"] = []
    review = client.post(
        "/api/v1/review", json={"original": extracted, "corrected": corrected, "confirmed": True}
    )
    assert review.status_code == 200
    reviewed = review.json()
    assert reviewed["original"]["document"]["total"] == "140.00"
    assert reviewed["corrected"]["total"] == "12.50"
    csv = client.post("/api/v1/export/csv", json=reviewed)
    assert csv.status_code == 200
    assert "12.50" in csv.text
    exported = client.post("/api/v1/export/json", json=reviewed)
    assert exported.status_code == 200
    assert exported.json()["confirmed"] is True


def test_confirmation_required(client: TestClient, png: bytes) -> None:
    original = _upload(client, png)
    payload = {
        "original": original,
        "corrected": original["document"],
        "confirmed": False,
        "issues": [],
    }
    assert client.post("/api/v1/export/csv", json=payload).status_code == 409


def test_bad_upload_and_explicit_live_opt_in(client: TestClient, png: bytes, monkeypatch) -> None:
    assert (
        client.post(
            "/api/v1/extract", files={"file": ("bad.pdf", b"bad", "application/pdf")}
        ).status_code
        == 415
    )
    monkeypatch.delenv("ALLOW_PAID_AI", raising=False)
    response = client.post(
        "/api/v1/extract", data={"mode": "openai"}, files={"file": ("sample.png", png, "image/png")}
    )
    assert response.status_code == 503


def test_batch_partial_failures(client: TestClient, png: bytes) -> None:
    files = [
        ("files", ("a.png", png, "image/png")),
        ("files", ("bad.txt", b"not an image", "text/plain")),
    ]
    result = client.post("/api/v1/batch", files=files)
    assert result.status_code == 200
    assert result.json()["success_count"] == 1
    assert result.json()["failure_count"] == 1


def test_csv_formula_injection(client: TestClient, png: bytes) -> None:
    original = _upload(client, png)
    corrected = dict(original["document"])
    corrected["issuer_name"] = '=HYPERLINK("evil")'
    payload = {"original": original, "corrected": corrected, "confirmed": True, "issues": []}
    result = client.post("/api/v1/export/csv", json=payload)
    assert result.status_code == 200
    assert "'=HYPERLINK" in result.text


def test_review_rejects_out_of_range_financial_amount(client: TestClient, png: bytes) -> None:
    original = _upload(client, png)
    corrected = dict(original["document"])
    corrected["subtotal"] = "123456789012345678901234567890.00"
    response = client.post(
        "/api/v1/review",
        json={"original": original, "corrected": corrected, "confirmed": True},
    )
    assert response.status_code == 422


def test_corrupt_png_returns_controlled_422(
    client: TestClient, png_with_bad_idat_crc: bytes
) -> None:
    response = client.post(
        "/api/v1/extract",
        files={"file": ("bad-crc.png", png_with_bad_idat_crc, "image/png")},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Unreadable or corrupt image"


def test_batch_isolates_corrupt_png(
    client: TestClient, png: bytes, png_with_bad_idat_crc: bytes
) -> None:
    response = client.post(
        "/api/v1/batch",
        files=[
            ("files", ("good.png", png, "image/png")),
            ("files", ("bad-crc.png", png_with_bad_idat_crc, "image/png")),
        ],
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success_count"] == 1
    assert body["failure_count"] == 1
    assert body["entries"][0]["success"] is True
    assert body["entries"][1]["success"] is False
    assert body["entries"][1]["error"] == "Unreadable or corrupt image"
