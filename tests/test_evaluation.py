"""All 30 documents are fictional and never claim real model performance."""

import pytest

from document_extractor.documents import prepare_document
from document_extractor.validation import validate_financial
from evaluation.runner import evaluate
from evaluation.synthetic import cases, render


def test_all_30_synthetic_cases() -> None:
    suite = cases()
    assert len(suite) == 30
    assert {case.layout for case in suite} == {
        "compact",
        "wide",
        "dense",
        "header-left",
        "centered",
    }
    assert {case.format for case in suite} == {"pdf", "png", "jpeg"}
    for case in suite:
        content_type = {"pdf": "application/pdf", "png": "image/png", "jpeg": "image/jpeg"}[
            case.format
        ]
        prepared = prepare_document(render(case), content_type, 5_242_880)
        assert prepared.image.startswith(b"\x89PNG")
        assert not validate_financial(case.expected)


@pytest.mark.asyncio
async def test_fixture_evaluation_has_no_fake_accuracy() -> None:
    report = await evaluate("fixture", 30, 0, 0)
    assert report["synthetic_cases_checked"] == 30
    assert report["model_field_accuracy"] is None
    assert report["cost_per_document_usd"] is None


@pytest.mark.asyncio
async def test_live_evaluation_counts_financial_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    from document_extractor.schemas import FinancialDocument
    from evaluation import runner

    class FakeProvider:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            self.last_usage = None

    async def fake_extract(*_args: object, **_kwargs: object) -> object:
        from document_extractor.schemas import ExtractionResult

        document = FinancialDocument(
            issuer_cnpj="11.222.333/0001-82",
            document_type="invoice",
            issuer_name="Synthetic",
            issue_date="2026-01-15",
            subtotal="100",
            total="999",
        )
        return ExtractionResult(
            mode="openai",
            document=document,
            issues=validate_financial(document),
            needs_review=True,
            processing_ms=2,
            notice="Synthetic fake, no network",
        )

    monkeypatch.setattr(runner, "OpenAIProvider", FakeProvider)
    monkeypatch.setattr(runner, "extract_document", fake_extract)
    monkeypatch.setenv("ALLOW_PAID_AI", "0")  # The fake never contacts any provider.
    report = await runner.evaluate("live", 1, 1.0, 0.5)
    assert report["financially_valid_percent"] == 0
    assert report["review_required_percent"] == 100


@pytest.mark.parametrize(
    ("actual_total", "expected_total", "expected_matches"),
    [
        ("10.00", "10", 7),
        ("10.01", "10.00", 6),
        (None, "10", 6),
        (None, None, 7),
    ],
)
def test_accuracy_uses_numeric_decimal_equality(
    actual_total: str | None, expected_total: str | None, expected_matches: int
) -> None:
    from evaluation.runner import _accuracy

    base: dict[str, object] = {
        "document_type": "invoice",
        "issuer_name": "Synthetic issuer",
        "issuer_cnpj": None,
        "issue_date": "2026-01-15",
        "document_number": "FAKE-001",
        "currency": "BRL",
        "total": expected_total,
    }
    actual = {**base, "total": actual_total}
    matched, total_fields = _accuracy(actual, base)
    assert matched == expected_matches
    assert total_fields == 7


@pytest.mark.asyncio
async def test_live_evaluation_does_not_estimate_cost_from_stale_usage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two offline mocked provider responses: usage present, then unavailable."""
    import json

    import httpx

    from document_extractor.providers import OpenAIProvider, response_json_schema
    from evaluation import runner

    monkeypatch.setenv("OPENAI_API_KEY", "fictional-test-key")
    monkeypatch.setenv("ALLOW_PAID_AI", "1")  # All requests use MockTransport.
    monkeypatch.setenv("AI_INPUT_USD_PER_MILLION", "1")
    monkeypatch.setenv("AI_OUTPUT_USD_PER_MILLION", "1")

    fields = {field: None for field in response_json_schema()["properties"] if field != "items"}
    fields.update({"document_type": "receipt", "total": "10", "items": []})
    count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal count
        count += 1
        response: dict[str, object] = {"choices": [{"message": {"content": json.dumps(fields)}}]}
        if count == 1:
            response["usage"] = {"prompt_tokens": 120, "completion_tokens": 80}
        return httpx.Response(200, json=response)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        monkeypatch.setattr(
            runner,
            "OpenAIProvider",
            lambda settings: OpenAIProvider(settings, client),
        )
        report = await runner.evaluate("live", 2, 1.0, 0.5)

    assert count == 2
    assert report["synthetic_cases_checked"] == 2
    assert report["cost_per_document_usd"] is None
