# README and badge inventory

**Scope:** `RamonRDR/ai-document-extractor`, PR #1 development branch. Audited from actual `pyproject.toml`, `src/`, `tests/`, `Dockerfile`, `LICENSE`, both Actions workflows, README files and the green [run 42407900020](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42407900020).

**Updated regression result:** 61 pytest passed, 0 failed, 0 skipped, 1 non-fatal warning. Synthetic evaluation validated 30 fictional fixtures. No real AI extraction accuracy, coverage percentage or provider billing measured.

| Category | Technology / check | Badge | Evidence and qualification |
| --- | --- | --- | --- |
| General | CI | Yes | .github/workflows/ci.yml; GitHub Actions run 42407900020 (verify + docker success) |
| General | Python 3.14 | Yes | pyproject.toml requires-python >=3.14,<3.15; ci.yml setup-python 3.14 |
| General | MIT License | Yes | LICENSE; pyproject.toml license=MIT |
| Stack / Infrastructure | FastAPI >=0.128 | Yes | pyproject.toml fastapi>=0.128,<1; src/document_extractor/api.py |
| Stack / Infrastructure | Pydantic v2 | Yes | pyproject.toml pydantic>=2.11,<3; schemas.py |
| Stack / Infrastructure | Uvicorn ASGI | Yes | pyproject.toml uvicorn>=0.35,<1; Dockerfile CMD |
| Stack / Infrastructure | httpx >=0.28 | Yes | pyproject.toml httpx>=0.28,<1; providers.py |
| Stack / Infrastructure | Pillow >=11.3 | Yes | pyproject.toml pillow>=11.3,<13; documents.py |
| Stack / Infrastructure | pypdfium2 >=5.14 | Yes | pyproject.toml pypdfium2>=5.14,<6; documents.py |
| Stack / Infrastructure | python-multipart >=0.0.20 | Yes | pyproject.toml python-multipart>=0.0.20,<1; FastAPI File/Form |
| Stack / Infrastructure | Docker build | Yes | Dockerfile; .github/workflows/ci.yml docker job success |
| AI / Integration | OpenAI API (opt-in adapter, live unverified) | Yes | providers.py OpenAIProvider; service.py ALLOW_PAID_AI gate; no paid E2E |
| AI / Integration | Structured outputs JSON Schema | Yes | providers.py response_json_schema() and JSON schema request; mocked integration test |
| Quality / Documentation | pytest 46 passing | Yes | GitHub Actions run 42741615175 verify logs: 61 passed, 1 warning, 0 failed/skipped; old badge count caused the subsequent documentation check to fail |
| Quality / Documentation | pytest-asyncio | Yes | pyproject.toml pytest-asyncio>=1.2,<2; async tests |
| Quality / Documentation | Ruff lint & format | Yes | ci.yml ruff check + format --check; green run |
| Quality / Documentation | mypy type checked | Yes | ci.yml mypy --ignore-missing-imports; strict tool.mypy; green run |
| Quality / Documentation | OpenAPI /docs | Yes | api.py FastAPI app, test_api.py GET /docs HTTP 200 |
| Quality / Documentation | 30 synthetic evaluation cases | Yes | evaluation/synthetic.py, tests/test_evaluation.py, CI evaluation report; not actual AI accuracy |
| Quality / Documentation | Python package build | Yes | pyproject.toml hatchling; ci.yml python -m build passed |
| Quality / Documentation | Feature branch format workflow | Yes | .github/workflows/format-branch.yml; run 42407893932 success |

## Exclusions from badge set

- **PostgreSQL, SQLite, Redis, pgvector, SQLAlchemy, Alembic, Docker Compose:** not present.
- **Node.js, TypeScript, React, Tailwind, ESLint, Prettier, Vitest, Playwright, PWA:** not present.
- **RAG, embeddings, MCP, tool-calling, OAuth, cloud spreadsheet APIs:** not implemented.
- **Test coverage, measured model accuracy, production deployment, security scan result:** no source of truth, so no badge.
- **OpenAI live extraction:** adapter implemented and mocked, but no paid real-provider execution is confirmed. Badge is explicitly opt-in.

## Test badge maintenance

1. GitHub Actions runs `pytest -q --junitxml=test-results.xml`.
2. The next step runs `python scripts/check_readme_badges.py --junitxml=test-results.xml`.
3. The script calculates **passed = tests - failures - errors - skipped**, confirms no test failures, verifies **21 identical badges across all three locales**, checks local links and asserts that the static pytest passing label matches the actual JUnit report.
4. When tests change, update the **three** README badge blocks together. If the count differs, CI fails rather than displaying an unverified green badge.
5. CI workflow status badges use the PR branch explicitly. **Once the PR is merged by the user**, update their branch parameters to `main` with the user's authorization. No workflow commits to `main`.

## Second audit checklist

- [x] Manifest versions cross-checked against badges.
- [x] Source modules and implemented integrations cross-checked against badges.
- [x] Dockerfile and both workflows cross-checked against badges.
- [x] CI results audited before using pytest / quality labels.
- [x] No datastore, migration, UI framework or fake performance metric added.
- [x] All three README variants share the identical badge block and the same section structure.
- [x] README badge/link check added to CI without changing business logic.
- [x] CI verified for README/badge validation: [run 42738578529](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42738578529), 46 pytest passes, three locales, 21 badges and green Docker build.

**Review policy:** no Codex Review requested without explicit approval; no merge performed.

## Initial Codex review remediation (2026-11-09)

Six review findings (one P1, five P2) were addressed on the PR branch: pre-parser request-size limit, image EXIF removal, Decimal range guards, subtotal-free reconciliation, stale browser review rejection and financial error metrics. New regression tests increased pytest cases from 46 to **61**. The static badge count was updated across all three README versions. The final green CI for this remediation must be recorded when available.
