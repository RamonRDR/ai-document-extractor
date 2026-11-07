# AI Document Extractor

[![CI](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml)

**English** · [Português](README.pt-BR.md) · [Español](README.es.md)

Portfolio-ready, stateless Python API for structured extraction and human review of one-page financial documents. Demonstrates FastAPI, multimodal structured output, Pydantic, Decimal-based financial validation, test automation and GitHub Actions.

> **Mode distinction:** Demo mode returns one **constant, fictional example**, regardless of input content. It does **not** perform OCR or AI extraction. Real model processing is only available after explicit opt-in. Never upload confidential material to a public deployment.

## Features

- PDF, PNG and JPEG uploads; magic-byte and MIME validation; one-page limit and bounded image processing.
- Explicit `demo` and `openai` provider modes via a replaceable adapter protocol.
- Structured JSON, nullable fields, origin indicators and automatic consistency warnings.
- CNPJ check digits, dates, decimal currency parsing, line-item/subtotal reconciliation, discounts, taxes and surcharges.
- Small browser review UI at `/`, plus correction, confirmation, CSV and JSON endpoints.
- Small batches (default max 5), per-file error isolation and a processing report.
- 30 fully synthetic examples across formats and layouts; deterministic regressions without paid calls.
- CI checks, distribution build and Docker image build; no deployment and no paid automated evaluations.

## Technology and architecture

Python 3.14, FastAPI, Pydantic v2, httpx, Pillow, pypdfium2 (permissive licensing), pytest, Ruff, mypy, Docker and GitHub Actions. See [architecture](docs/architecture.md), [v1 schema](docs/schema.md) and [ADR](docs/adr/0001-provider-and-renderer.md).

## Install and run

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn document_extractor.api:app --reload
```

Windows: `.venv\Scripts\activate`. Open `http://127.0.0.1:8000/` for review UI or `/docs` for interactive OpenAPI docs. Docker: `docker build -t ai-document-extractor .` then `docker run --rm -p 8000:8000 ai-document-extractor`.

## Configuration

See [`.env.example`](.env.example). The default is free demo mode with no secrets. For a **manually authorized** real provider call, export `ALLOW_PAID_AI=1` and `OPENAI_API_KEY`; send `mode=openai`. Use `AI_MODEL` and `AI_TIMEOUT_SECONDS` to adjust the model and timeout. Do not commit secrets. No live calls run in CI.

## Upload example

```bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@fictional-receipt.png;type=image/png" \
  -F "mode=demo"
```

Example abbreviated **demo** JSON (fictional; identical for any valid upload):

```json
{
  "mode": "demo",
  "document": {
    "document_type": "synthetic_receipt",
    "issuer_name": "Example Studio (FICTIONAL)",
    "issuer_cnpj": null,
    "issue_date": "2026-01-15",
    "total": "140.00",
    "items": [{"description": "Synthetic service", "quantity": "2", "unit_price": "75.00", "total": "150.00"}]
  },
  "needs_review": true,
  "notice": "DEMO ONLY: fixed fictional data. No AI extraction or OCR performed."
}
```

The actual response also contains document number, currency, adjustments, provenance, processing time and issues. See [schema details](docs/schema.md).

## Financial validation and human review

Send `{"original": <extraction-result>, "corrected": <edited-document>, "confirmed": true}` to `POST /api/v1/review`. Keep its response, then POST it to `/api/v1/export/csv` or `/api/v1/export/json`. Export without confirmation returns HTTP 409. The browser UI handles this flow and highlights warnings. The API retains separate original and corrected records in the response, not in storage. CSV text is protected against spreadsheet-formula injection.

## Batch, tests and evaluation

Use `POST /api/v1/batch` with several `files` fields and `mode=demo` (or explicitly authorized `openai`). Each item has an index and independent success/error. The result contains totals.

```bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture --report evaluation-report.json
python -m build
```

The **30-case fixture evaluation** validates decoding, schemas and financial rules. Its model accuracy and model cost are `null`: it does not run real AI. Optional, *manual* real-model evaluation requires `EVAL_LIVE=1`, `ALLOW_PAID_AI=1`, a provider key, and explicit positive dollar reservation parameters. Example for an authorized budget: `python -m evaluation.runner --mode live --max-documents 3 --max-usd-per-document 0.20 --budget-usd 0.60`. Budget parameters reserve an estimated ceiling, **not enforce actual provider billing**. Model costs can optionally be estimated from returned token usage by setting `AI_INPUT_USD_PER_MILLION` and `AI_OUTPUT_USD_PER_MILLION` to current model rates. Unavailable usage leaves costs null. Use real provider billing for authoritative costs. Never run this command automatically.

## CI / security / limitations

GitHub Actions on PRs and pushes performs Ruff, formatting, typing, tests, schema checks, deterministic evaluation, wheel/sdist build and Docker build on hosted runners. It never uses the user's machine or triggers paid AI. A feature-branch-only formatter may normalize committed formatting; it does not touch `main`.

See [privacy and threat model](docs/privacy.md). This is not a production accounting platform: no authentication, persistence, scalable worker, malware scanner, production rate limiter, multipage support or field-level evidence boxes. PDF input parsing should be sandboxed for unknown traffic. The prompt treats document text as untrusted. Privacy, licensing and cross-check accuracy must be reviewed before production use.

## License

Application code: [MIT](LICENSE). Third-party dependencies retain their own licenses, including pypdfium2/PDFium license notices.
