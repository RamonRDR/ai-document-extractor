"""Optional paid model evaluation and deterministic fixture/validation checks.

Default CI mode never calls any provider and never claims model accuracy.
"""

import argparse
import asyncio
import json
import os
from decimal import Decimal
from pathlib import Path
from time import perf_counter

from document_extractor.documents import prepare_document
from document_extractor.providers import OpenAIProvider
from document_extractor.service import extract_document
from document_extractor.settings import Settings
from document_extractor.validation import validate_financial

from .synthetic import cases, render


def _accuracy(actual: dict[str, object], expected: dict[str, object]) -> tuple[int, int]:
    fields = (
        "document_type",
        "issuer_name",
        "issuer_cnpj",
        "issue_date",
        "document_number",
        "currency",
        "total",
    )
    return (sum(actual.get(field) == expected.get(field) for field in fields), len(fields))


async def evaluate(
    mode: str, limit: int, budget: float, rate_per_document: float
) -> dict[str, object]:
    selected = cases()[:limit]
    started = perf_counter()
    checked = 0
    valid = 0
    flagged = 0
    matched = 0
    total_fields = 0
    latency: list[int] = []
    estimated_cost = Decimal("0")
    costed = 0
    input_rate = Decimal(os.getenv("AI_INPUT_USD_PER_MILLION", "0"))
    output_rate = Decimal(os.getenv("AI_OUTPUT_USD_PER_MILLION", "0"))
    provider = OpenAIProvider(Settings.from_env()) if mode == "live" else None
    for index, case in enumerate(selected):
        data = render(case)
        mime = {"png": "image/png", "jpeg": "image/jpeg", "pdf": "application/pdf"}[case.format]
        prepare_document(data, mime, Settings.from_env().max_upload_bytes)
        if mode == "live":
            if (index + 1) * rate_per_document > budget:
                raise ValueError("Budget reservation limit reached before provider call")
            assert provider is not None
            result = await extract_document(data, mime, "openai", Settings.from_env(), provider)
            actual = result.document
            latency.append(result.processing_ms)
            if provider.last_usage and input_rate > 0 and output_rate > 0:
                usage = provider.last_usage
                estimated_cost += (
                    Decimal(usage["prompt_tokens"]) * input_rate
                    + Decimal(usage["completion_tokens"]) * output_rate
                ) / Decimal(1_000_000)
                costed += 1
            flagged += int(result.needs_review)
            current, available = _accuracy(
                actual.model_dump(mode="json"), case.expected.model_dump(mode="json")
            )
            matched += current
            total_fields += available
        else:
            actual = case.expected
            flagged += int(bool(validate_financial(actual)))
        # Structural missing/inferred warnings require review; financial errors fail validity.
        valid += int(not any(issue.severity == "error" for issue in validate_financial(actual)))
        checked += 1
    output: dict[str, object] = {
        "mode": mode,
        "synthetic_cases_checked": checked,
        "format_counts": {
            extension: sum(case.format == extension for case in selected)
            for extension in ("png", "jpeg", "pdf")
        },
        "financially_valid_percent": round(100 * valid / checked, 2) if checked else None,
        "review_required_percent": round(100 * flagged / checked, 2) if checked else None,
        "elapsed_ms": round((perf_counter() - started) * 1000),
        "model_field_accuracy": round(100 * matched / total_fields, 2)
        if mode == "live" and total_fields
        else None,
        "mean_document_processing_ms": round(sum(latency) / len(latency)) if latency else None,
        "cost_per_document_usd": (
            float(round(estimated_cost / checked, 6))
            if mode == "live" and costed == checked and checked > 0
            else None
        ),
        "caveat": "fixture mode does not run a model or measure extraction accuracy"
        if mode != "live"
        else (
            "live mode uses provider; reserved budget is a user-supplied ceiling, "
            "not measured billing; token-price estimate if configured"
        ),
    }
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixture", "live"), default="fixture")
    parser.add_argument("--max-documents", type=int, default=30)
    parser.add_argument("--budget-usd", type=float, default=0)
    parser.add_argument("--max-usd-per-document", type=float, default=0)
    parser.add_argument("--report", default="evaluation-report.json")
    arguments = parser.parse_args()
    if not 1 <= arguments.max_documents <= 30:
        parser.error("--max-documents must be 1 through 30")
    if arguments.mode == "live":
        if os.getenv("ALLOW_PAID_AI") != "1" or os.getenv("EVAL_LIVE") != "1":
            parser.error("Live evaluation requires ALLOW_PAID_AI=1 and EVAL_LIVE=1")
        if arguments.budget_usd <= 0 or arguments.max_usd_per_document <= 0:
            parser.error(
                "Live evaluation requires positive explicit budget and reservation per document"
            )
        if arguments.max_documents * arguments.max_usd_per_document > arguments.budget_usd:
            parser.error("Budget must cover reserved ceiling for all documents")
    report = asyncio.run(
        evaluate(
            arguments.mode,
            arguments.max_documents,
            arguments.budget_usd,
            arguments.max_usd_per_document,
        )
    )
    path = Path(arguments.report)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
