"""All 30 documents are fictional and never claim real model performance."""

import pytest

from document_extractor.documents import prepare_document
from document_extractor.validation import validate_financial
from evaluation.runner import evaluate
from evaluation.synthetic import cases, render


def test_all_30_synthetic_cases() -> None:
    suite = cases()
    assert len(suite) == 30
    assert {case.layout for case in suite} == {"compact", "wide", "dense", "header-left", "centered"}
    assert {case.format for case in suite} == {"pdf", "png", "jpeg"}
    for case in suite:
        content_type = {"pdf": "application/pdf", "png": "image/png", "jpeg": "image/jpeg"}[case.format]
        prepared = prepare_document(render(case), content_type, 5_242_880)
        assert prepared.image.startswith(b"\x89PNG")
        assert not validate_financial(case.expected)


@pytest.mark.asyncio
async def test_fixture_evaluation_has_no_fake_accuracy() -> None:
    report = await evaluate("fixture", 30, 0, 0)
    assert report["synthetic_cases_checked"] == 30
    assert report["model_field_accuracy"] is None
    assert report["cost_per_document_usd"] is None
