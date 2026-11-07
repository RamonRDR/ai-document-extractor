# Technical self-review (2026-11-07)

## Verified in hosted CI
- Python 3.14 dependency installation, Ruff, formatter, mypy, pytest (45 tests before final hardening), JSON schema checks, deterministic 30-case regression and packaging passed on the pre-hardening commit.
- Docker image build passed on GitHub-hosted runners.
- A subsequent hardening commit added strict output-key checks, token usage estimates, CNPJ mask validation and a provider-response test; it must pass CI before final review readiness.

## Security review
- Demo mode uses **fixed fictional** values; not OCR, not document extraction.
- Paid OpenAI path requires both an explicit API mode and environment opt-in. No provider keys are shipped, and no live calls run in CI.
- Document data is processed only in memory, with file-type, page-count, upload byte and pixel limits. No documents are checked into the repository.
- User-provided document content is treated as untrusted. The adapter never executes commands from it, and the prompt explicitly ignores embedded instructions.
- Export requires a confirmed review. CSV fields guard against formula injection.
- Provider HTTP failures, malformed structured responses and timeouts are mapped to controlled errors.

## Open risks and scope limitations
- This is a portfolio demonstration, **not** a production service. It has no authentication, rate limiting, antivirus scanning, OS sandbox for PDF parsing, tenant isolation, durable storage or evidence-coordinate highlighting.
- A human must still verify the model's extraction. Derived origin flags indicate model-provided fields, not ground-truth certainty.
- The live model's quality and billing were **not** measured because no external paid call was authorized. Fixture CI numbers are not AI accuracy metrics.
- Estimated token cost requires correct rates supplied by the operator and is not a billing cap.
- Single-page documents only. Networked deployment of this demo with sensitive data is not recommended.

## Final gates
1. CI checks green for the final branch head.
2. Keep pull request open with main untouched.
3. No Codex Review request until explicit user approval.
4. Correct any eventual reviewer issues and repeat CI.
5. Merge only after explicit user approval.
