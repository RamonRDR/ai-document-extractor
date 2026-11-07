"""Multimodal provider boundary. No paid calls in demo mode or unit tests."""

import base64
import json
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from .documents import PreparedDocument
from .prompts import EXTRACTION_PROMPT
from .schemas import FinancialDocument, Origin
from .settings import Settings


class ProviderError(Exception):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code


class ExtractionProvider(Protocol):
    async def extract(self, document: PreparedDocument) -> FinancialDocument: ...


SCALAR_FIELDS = (
    "document_type",
    "issuer_name",
    "issuer_cnpj",
    "issue_date",
    "document_number",
    "currency",
    "subtotal",
    "discount",
    "tax",
    "surcharge",
    "total",
)
ITEM_FIELDS = ("description", "quantity", "unit_price", "total")


def _nullable_string() -> dict[str, Any]:
    return {"type": ["string", "null"]}


def response_json_schema() -> dict[str, Any]:
    item = {
        "type": "object",
        "properties": {field: _nullable_string() for field in ITEM_FIELDS},
        "required": list(ITEM_FIELDS),
        "additionalProperties": False,
    }
    fields: dict[str, Any] = {field: _nullable_string() for field in SCALAR_FIELDS}
    fields["items"] = {"type": "array", "items": item}
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
    }


def mark_provenance(values: dict[str, Any], origin: Origin) -> dict[str, Any]:
    marked = dict(values)
    marked["provenance"] = {
        field: origin if marked.get(field) not in (None, "", []) else Origin.MISSING
        for field in (*SCALAR_FIELDS, "items")
    }
    return marked


class DemoProvider:
    """Constant synthetic example, NEVER document-specific extraction or OCR."""

    async def extract(self, document: PreparedDocument) -> FinancialDocument:
        del document
        fields: dict[str, Any] = {
            "document_type": "synthetic_receipt",
            "issuer_name": "Example Studio (FICTIONAL)",
            "issuer_cnpj": None,
            "issue_date": "2026-01-15",
            "document_number": "DEMO-001",
            "currency": "BRL",
            "subtotal": "150.00",
            "discount": "10.00",
            "tax": None,
            "surcharge": None,
            "total": "140.00",
            "items": [
                {
                    "description": "Synthetic service",
                    "quantity": "2",
                    "unit_price": "75.00",
                    "total": "150.00",
                }
            ],
        }
        return FinancialDocument.model_validate(mark_provenance(fields, Origin.DEMO))


class OpenAIProvider:
    """Explicit, budget-gated OpenAI-compatible JSON-schema extraction adapter."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client

    async def extract(self, document: PreparedDocument) -> FinancialDocument:
        if not self.settings.api_key:
            raise ProviderError("OPENAI_API_KEY not configured", 503)
        url = "https://api.openai.com/v1/chat/completions"
        image_url = "data:image/png;base64," + base64.b64encode(document.image).decode("ascii")
        request = {
            "model": self.settings.ai_model,
            "temperature": 0,
            "max_completion_tokens": 2500,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "financial_document_v1",
                    "strict": True,
                    "schema": response_json_schema(),
                },
            },
            "messages": [
                {"role": "system", "content": EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract only document data from the attached image.",
                        },
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
        }
        try:
            if self.client is None:
                async with httpx.AsyncClient(
                    timeout=self.settings.ai_timeout_seconds, follow_redirects=False
                ) as client:
                    response = await client.post(
                        url,
                        headers={"Authorization": f"Bearer {self.settings.api_key}"},
                        json=request,
                    )
            else:
                response = await self.client.post(
                    url, headers={"Authorization": f"Bearer {self.settings.api_key}"}, json=request
                )
            response.raise_for_status()
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise ValueError("Missing provider JSON")
            fields = json.loads(content)
            if not isinstance(fields, dict):
                raise ValueError("Expected object response")
            return FinancialDocument.model_validate(mark_provenance(fields, Origin.EXTRACTED))
        except httpx.TimeoutException as exc:
            raise ProviderError("AI provider timed out", 504) from exc
        except httpx.HTTPError as exc:
            raise ProviderError("AI provider unavailable or rejected the request") from exc
        except (KeyError, IndexError, TypeError, ValueError, ValidationError) as exc:
            raise ProviderError("AI provider returned an invalid structured response") from exc
