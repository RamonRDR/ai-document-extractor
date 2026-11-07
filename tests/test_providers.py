"""Real adapter is tested with an in-process HTTP mock only."""

import json

import httpx
import pytest

from document_extractor.documents import PreparedDocument
from document_extractor.providers import (
    DemoProvider,
    OpenAIProvider,
    ProviderError,
    response_json_schema,
)
from document_extractor.settings import Settings


def settings() -> Settings:
    return Settings(
        api_key="fake-test-token",
        ai_model="test-model",
        ai_timeout_seconds=1,
        max_upload_bytes=5_242_880,
        max_batch_files=5,
    )


@pytest.mark.asyncio
async def test_fixed_demo_is_explicit() -> None:
    doc = await DemoProvider().extract(PreparedDocument(b"x", "image/png"))
    assert doc.issuer_name == "Example Studio (FICTIONAL)"
    assert str(doc.total) == "140.00"


@pytest.mark.asyncio
async def test_structured_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        assert payload["response_format"]["type"] == "json_schema"
        assert payload["messages"][0]["role"] == "system"
        values = {field: None for field in response_json_schema()["properties"] if field != "items"}
        values.update({"document_type": "receipt", "total": "30.50", "items": []})
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": json.dumps(values)}}],
                "usage": {"prompt_tokens": 120, "completion_tokens": 80},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        provider = OpenAIProvider(settings(), client)
        doc = await provider.extract(PreparedDocument(b"data", "image/png"))
    assert str(doc.total) == "30.50"
    assert provider.last_usage == {"prompt_tokens": 120, "completion_tokens": 80}


@pytest.mark.asyncio
async def test_invalid_response() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda req: httpx.Response(
                200, json={"choices": [{"message": {"content": "{BAD JSON"}}]}
            )
        )
    ) as client:
        with pytest.raises(ProviderError, match="invalid structured"):
            await OpenAIProvider(settings(), client).extract(PreparedDocument(b"x", "image/png"))


@pytest.mark.asyncio
async def test_provider_down() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda req: httpx.Response(503))
    ) as client:
        with pytest.raises(ProviderError, match="unavailable"):
            await OpenAIProvider(settings(), client).extract(PreparedDocument(b"x", "image/png"))


@pytest.mark.asyncio
async def test_provider_timeout() -> None:
    def raise_timeout(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("synthetic timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(raise_timeout)) as client:
        with pytest.raises(ProviderError, match="timed out"):
            await OpenAIProvider(settings(), client).extract(PreparedDocument(b"x", "image/png"))
