<div align="center">

# AI Document Extractor 📄

**Turn financial documents into structured data, verify every value, and export with human oversight.**

[🇺🇸 English](README.md) · [🇧🇷 Português](README.pt-BR.md) · [🇪🇸 Español](README.es.md)

<!-- BADGES:START -->
[![CI](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml/badge.svg?branch=feat%2Fdocument-extractor-full-implementation)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation)
![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB)
[![MIT License](https://img.shields.io/badge/License-MIT-2ea44f)](LICENSE)

![FastAPI >=0.128](https://img.shields.io/badge/FastAPI-0.128%2B-009688)
![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063)
![Uvicorn ASGI](https://img.shields.io/badge/Uvicorn-ASGI-4051B5)
![httpx >=0.28](https://img.shields.io/badge/httpx-0.28%2B-4479A1)
![Pillow >=11.3](https://img.shields.io/badge/Pillow-11.3%2B-5C5C5C)
![pypdfium2 >=5.14](https://img.shields.io/badge/pypdfium2-5.14%2B-6D3A88)
![python-multipart >=0.0.20](https://img.shields.io/badge/python--multipart-0.0.20%2B-6A5ACD)
![Docker Build](https://img.shields.io/badge/Docker-build%20validated-2496ED)

![OpenAI API optional](https://img.shields.io/badge/OpenAI%20API-opt--in%20adapter-5A6872)
![Structured outputs](https://img.shields.io/badge/Structured%20Outputs-JSON%20Schema-7E57C2)

![pytest 61 passing](https://img.shields.io/badge/pytest-61%20passing-0A9EDC)
![pytest-asyncio](https://img.shields.io/badge/pytest--asyncio-enabled-0A9EDC)
![Ruff lint and format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy type checked](https://img.shields.io/badge/mypy-type%20checked-2A6DB4)
![OpenAPI documented](https://img.shields.io/badge/OpenAPI-%2Fdocs%20validated-6BA539)
![30 synthetic fixtures](https://img.shields.io/badge/Synthetic%20Evaluation-30%20fixtures-607D8B)
![Package build](https://img.shields.io/badge/Package%20Build-wheel%20%2B%20sdist-455A64)
[![Feature branch formatting](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml/badge.svg?branch=feat%2Fdocument-extractor-full-implementation)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation)

<!-- BADGES:END -->

</div>

> **Project status:** Implementation in [PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1), with six initial Codex findings addressed in the PR branch; awaiting follow-up review and authorized merge. [CI for the development branch](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation) is green. No deployment or published package.

## Overview

A stateless, human-reviewed API for single-page financial documents. It converts validated PDF, PNG, or JPEG uploads into structured financial fields, checks arithmetic consistency, and requires human confirmation before CSV/JSON export. It demonstrates backend Python, financial automation, typed REST contracts, multimodal adapter design, and hosted CI for international software-engineering portfolios.

**Two distinct modes:** `demo` returns the **same fixed fictional record** for every valid input; it does **not** read the document via OCR or AI. `openai` is an implemented, **opt-in** multimodal adapter; real paid-model extraction has **not** been exercised or benchmarked.

## Implemented features

- One-page PDF, PNG and JPEG; magic-byte/MIME agreement, upload-size limits, PDF rendering, image verification and pixel limits.
- A replaceable provider protocol, a deterministic fictional demo and an optional OpenAI-compatible multimodal integration using structured JSON Schema output.
- Nullable Pydantic v2 contracts, field provenance (`extracted`, `inferred`, `missing` or `demo`), timestamps and review warnings.
- Brazilian CNPJ verification, date parsing, `Decimal` currency amounts, item totals, subtotals, discounts, taxes and surcharges.
- Simple browser interface for correction/confirmation; original and corrected data remain distinct in the review response.
- CSV and JSON export after explicit human confirmation; CSV formula-prefix hardening.
- Batches of up to five documents by default, independent per-file errors and result counts.
- 30 synthetic PDF/image fixtures, mocked model tests, packaging checks and GitHub-hosted automation.

## Technology stack

| Layer | Real implementation |
| --- | --- |
| Runtime | **Python 3.14**, package version `0.1.0` |
| API and data | FastAPI **0.128+** (declared minimum), Pydantic **v2** (2.11+), Uvicorn ASGI, python-multipart **0.0.20+** |
| Documents and HTTP | pypdfium2 **5.14+** for PDFs, Pillow **11.3+** for images, httpx **0.28+** for provider requests |
| AI boundary | OpenAI API adapter with multimodal image input and strict JSON Schema structured output, disabled by default; external live extraction not validated |
| Quality | pytest, pytest-asyncio, Ruff lint/format, strict mypy, 30 deterministic synthetic evaluation cases |
| Automation | GitHub Actions, Hatchling build of wheel/sdist, Docker image build, feature-branch formatting |

Version numbers with `+` are **declared lower bounds**, not claims that one exact release is pinned. The manifest may allow higher compatible releases. No database, Redis, Alembic, Docker Compose, RAG, embeddings or MCP is used.

## Architecture

The flow is **upload → validation → PDF/image preparation → selected provider → Pydantic contract → financial checks → human correction → confirmed export**. No database or document storage is involved. See the [architecture diagram](docs/architecture.md), [schema guide](docs/schema.md), and [provider/renderer ADR](docs/adr/0001-provider-and-renderer.md).

## Requirements

Python **3.14** and pip. Docker Engine is optional. A real model key is **not** needed to run the demo, tests or CI. Do not use private documents in a public demo.

## Installation

~~~bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
~~~

On Windows, activate with `.venv\Scripts\activate`. Optional container build: `docker build -t ai-document-extractor .`.

## Configuration

See [`.env.example`](.env.example). It is a reference file; the app reads **environment variables**, it does not automatically load the file.

| Variable | Purpose |
| --- | --- |
| `ALLOW_PAID_AI` | Default `0`; must be `1` for the live route |
| `OPENAI_API_KEY` | Secret for authorized real extraction; never commit it |
| `AI_MODEL` | Default `gpt-4o-mini` (configured model name, not a live validation result) |
| `AI_TIMEOUT_SECONDS` | Provider timeout (default 20 seconds) |
| `MAX_UPLOAD_BYTES` | Per-file upload limit (default 5,242,880 bytes) |
| `MAX_BATCH_FILES` | Per-request file limit (default 5) |
| `EVAL_LIVE` | Extra manual opt-in for live evaluation, default `0` |
| `AI_INPUT_USD_PER_MILLION` / `AI_OUTPUT_USD_PER_MILLION` | Optional user-provided token rates for a cost **estimate**, never a billing limit |

No secrets are used by the CI workflows. Real extraction can incur usage charges and sends the rendered document image to the provider.

## Run and interface

~~~bash
uvicorn document_extractor.api:app --reload
# Docker alternative:
docker run --rm -p 8000:8000 ai-document-extractor
~~~

The local browser UI is at `http://127.0.0.1:8000/`. REST endpoints:

| Endpoint | Function |
| --- | --- |
| `GET /health` | Basic status |
| `GET /docs` | Swagger UI and automatic FastAPI documentation |
| `GET /openapi.json` | OpenAPI schema |
| `POST /api/v1/extract` | One document, `mode=demo` or `mode=openai` |
| `POST /api/v1/batch` | Multiple uploaded files, independent results |
| `POST /api/v1/review` | Submit original record, corrected fields and confirmation |
| `POST /api/v1/export/csv` / `POST /api/v1/export/json` | Download reviewed, confirmed data |

## Usage example

~~~bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@fictional-receipt.png;type=image/png" \
  -F "mode=demo"
~~~

Abbreviated **synthetic demo** response, not extracted from the input file:

~~~json
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
~~~

The actual response includes currency, document number, subtotal/adjustments, provenance, warnings and processing duration. [Full schema details](docs/schema.md).

## Financial validation and human review

CNPJ check digits and format, dates, amounts, quantities, line-item products and subtotal/adjustment reconciliation generate review issues rather than quietly rewriting extracted values. Missing data is null, not invented. Submit `{"original": <extraction-result>, "corrected": <edited-document>, "confirmed": true}` to `POST /api/v1/review`; then POST its output to `/api/v1/export/csv` or `/api/v1/export/json`. Without confirmation export returns **HTTP 409**. The browser UI supports the same workflow.

## Batch processing

Send multiple multipart `files` to `POST /api/v1/batch`; each response entry has its index, success, result or error. Counts distinguish successes and failures. Limit defaults to five files, with a size limit for each.

## Automated tests and evaluation

~~~bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture --report evaluation-report.json
python -m build
~~~

The documented **61 passing tests** were executed in [GitHub Actions run 42741615175](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42741615175) (61 passed, 0 failed, 0 skipped, one warning; that run subsequently stopped at the stale badge check, since corrected). The 30 fully fictional fixtures exercise decoding, schemas and financial rules; their report does **not** claim model extraction accuracy or actual model cost. Live provider evaluation is manual, gated by `EVAL_LIVE=1`, `ALLOW_PAID_AI=1`, a key and explicit nonzero budget parameters. For an **already authorized** budget, the command shape is `python -m evaluation.runner --mode live --max-documents 3 --max-usd-per-document 0.20 --budget-usd 0.60`. Budget parameters reserve an operator estimate and do **not** enforce actual vendor billing.

## GitHub Actions and badge maintenance

The [CI workflow](.github/workflows/ci.yml) runs Ruff, formatting, mypy, pytest, strict schema checks, deterministic fixtures, wheel/sdist build and a separate Docker build job. The [feature-branch formatter](.github/workflows/format-branch.yml) can normalize files only on `feat/**` branches and does not commit into `main`. CI uses hosted runners and **never calls paid models**.

The **pytest badge is static and auditable**: [`scripts/check_readme_badges.py`](scripts/check_readme_badges.py) compares its passing count against the actual CI JUnit XML report and checks all three READMEs. A test-count change must update the three copies and pass CI before the badge can be considered current. The dynamic CI/format badges target the development branch while PR #1 is open; after merge, badge URLs should target `main`. Full [badge inventory](docs/badges.md).

## Security and privacy

Treat document contents as untrusted; model prompts are instructions only to the provider, never executable actions. File type, MIME, page count, byte/pixel bounds, provider timeout and formula-injection protection reduce risk. Requests are processed without durable document storage. **Starlette may spool multipart file parts temporarily to the OS disk**; a bounded ASGI request-size gate runs before multipart parsing, and normalized provider-bound images have EXIF/GPS metadata stripped. No secrets, genuine financial documents, paid calls or publication are bundled. Review the [privacy/threat model](docs/privacy.md) before sharing or running the service.

## Known limitations and future work

One page only; no authentication, rate limiter, malware scanner, sandboxed PDF worker, document persistence, tenant isolation, queues or field-level source bounding boxes. The optional live model has not been benchmarked against ground truth, and the human must verify every result. Production hardening would require sandboxing, access controls and real model evaluation. This project is **not deployed** as a public accounting service.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `src/document_extractor/api.py` / `ui.html` | HTTP endpoints and human review interface |
| `src/document_extractor/documents.py` | File validation and PDF/image rendering |
| `src/document_extractor/providers.py` / `prompts.py` | Demo/live providers, schema request and prompt |
| `src/document_extractor/schemas.py` / `validation.py` / `finance.py` | Typed fields and financial checks |
| `evaluation/` / `tests/` | Synthetic evaluation and automated tests |
| `scripts/check_readme_badges.py` | JUnit-backed README badge consistency validation |
| `.github/workflows/` | CI and feature-branch formatter |
| `docs/` | Architecture, schemas, ADR, privacy, technical and badge audits |

## Contributing

Open an issue or PR describing the proposed change; keep tests, documentation and all language versions aligned. Run Ruff, mypy and pytest first. Never commit personal financial data, tokens or secrets. The [project PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1) has addressed the six findings from the initial Codex Review and awaits follow-up verification and an authorized merge.

## License

Application source: [MIT License](LICENSE), copyright 2026 Ramon Rodriguez. Dependencies retain their own licenses, including PDFium/pypdfium2. No commercial support or production security guarantee is implied.
