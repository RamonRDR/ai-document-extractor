"""Orchestrate bounded validation, provider extraction and financial review."""

import os
from time import perf_counter
from typing import Literal

from .documents import prepare_document
from .prompts import PROMPT_VERSION
from .providers import DemoProvider, ExtractionProvider, OpenAIProvider, ProviderError
from .schemas import ExtractionResult
from .settings import Settings
from .validation import validate_financial


async def extract_document(
    data: bytes,
    content_type: str | None,
    mode: Literal["demo", "openai"],
    settings: Settings,
    provider: ExtractionProvider | None = None,
) -> ExtractionResult:
    start = perf_counter()
    prepared = prepare_document(data, content_type, settings.max_upload_bytes)
    if mode == "openai":
        if os.getenv("ALLOW_PAID_AI", "0") != "1":
            raise ProviderError("Live AI is disabled; set ALLOW_PAID_AI=1 to opt in", 503)
        used_provider = provider or OpenAIProvider(settings)
        notice = "Live AI extraction. Document image transmitted to the configured provider."
    else:
        used_provider = provider or DemoProvider()
        notice = "DEMO ONLY: fixed fictional data. No AI extraction or OCR performed."
    document = await used_provider.extract(prepared)
    issues = validate_financial(document)
    return ExtractionResult(
        mode=mode,
        document=document,
        issues=issues,
        needs_review=bool(issues) or mode == "demo",
        processing_ms=round((perf_counter() - start) * 1000),
        prompt_version=PROMPT_VERSION,
        notice=notice,
    )
