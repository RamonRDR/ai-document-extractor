"""Bound the raw multipart body before FastAPI sees it, even without Content-Length."""

import pytest
from fastapi.testclient import TestClient

from document_extractor.api import app


@pytest.mark.parametrize("endpoint", ["/api/v1/extract", "/api/v1/batch"])
def test_large_multipart_rejected_before_parser(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, endpoint: str
) -> None:
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "1024")
    monkeypatch.setenv("MAX_BATCH_FILES", "2")
    form_name = "file" if endpoint.endswith("extract") else "files"
    response = client.post(
        endpoint,
        files={form_name: ("huge.png", b"X" * 200_000, "image/png")},
    )
    assert response.status_code == 413
    assert "request body exceeds" in response.json()["detail"]


@pytest.mark.asyncio
async def test_streamed_multipart_enforced_without_content_length(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "1024")
    messages = [
        {"type": "http.request", "body": b"A" * 40_000, "more_body": True},
        {"type": "http.request", "body": b"B" * 40_000, "more_body": False},
    ]
    replies: list[dict] = []

    async def receive() -> dict:
        return messages.pop(0)

    async def send(message: dict) -> None:
        replies.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/extract",
        "raw_path": b"/api/v1/extract",
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"multipart/form-data; boundary=ignored")],
        "client": ("test", 123),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    assert replies[0]["type"] == "http.response.start"
    assert replies[0]["status"] == 413
    assert messages == []
