"""Bound multipart request bytes before Starlette parses or spools upload files.

Uploads can still be spooled temporarily by Starlette; see docs/privacy.md.
"""

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .settings import Settings

# Allow multipart framing and ordinary field names in addition to file bytes.
MULTIPART_OVERHEAD_PER_FILE = 64 * 1024


class UploadRequestLimitMiddleware:
    """Pre-read up to the configured size, then replay to the multipart parser."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or scope["method"] != "POST":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        if path not in ("/api/v1/extract", "/api/v1/batch"):
            await self.app(scope, receive, send)
            return

        settings = Settings.from_env()
        number_of_files = 1 if path == "/api/v1/extract" else settings.max_batch_files
        max_body = number_of_files * (settings.max_upload_bytes + MULTIPART_OVERHEAD_PER_FILE)

        headers = dict(scope.get("headers", []))
        if b"content-length" in headers:
            try:
                length = int(headers[b"content-length"])
            except ValueError:
                await JSONResponse({"detail": "Invalid Content-Length"}, status_code=400)(
                    scope, receive, send
                )
                return
            if length < 0 or length > max_body:
                await JSONResponse(
                    {"detail": "Multipart request body exceeds configured limit"},
                    status_code=413,
                )(scope, receive, send)
                return

        chunks: list[bytes] = []
        size = 0
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            if event["type"] != "http.request":
                continue
            chunk = event.get("body", b"")
            size += len(chunk)
            if size > max_body:
                await JSONResponse(
                    {"detail": "Multipart request body exceeds configured limit"},
                    status_code=413,
                )(scope, receive, send)
                return
            chunks.append(chunk)
            if not event.get("more_body", False):
                break

        index = 0

        async def replay() -> Message:
            nonlocal index
            if index < len(chunks):
                part = chunks[index]
                index += 1
                return {
                    "type": "http.request",
                    "body": part,
                    "more_body": index < len(chunks),
                }
            return await receive()

        await self.app(scope, replay, send)
