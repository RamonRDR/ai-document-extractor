"""Provider response must satisfy all required structured-output keys."""

import json

import httpx
import pytest

from document_extractor.documents import PreparedDocument
from document_extractor.providers import OpenAIProvider, ProviderError
from document_extractor.settings import Settings


@pytest.mark.asyncio
async def test_missing_provider_fields_rejected() -> None:
    config = Settings(
        api_key="fake-test-token",
        ai_model="test",
        ai_timeout_seconds=1,
        max_upload_bytes=5_242_880,
        max_batch_files=5,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps({"total": "10.00"})}}]},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ProviderError, match="invalid structured response"):
            await OpenAIProvider(config, client).extract(PreparedDocument(b"X", "image/png"))
