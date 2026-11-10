# Technical self-review (2026-11-07)

## Verified in hosted CI
- Python 3.14 dependency installation, Ruff, formatter, mypy, pytest (45 tests before final hardening), JSON schema checks, deterministic 30-case regression and packaging passed on the pre-hardening commit.
- Docker image build passed on GitHub-hosted runners.
- A subsequent hardening commit added strict output-key checks, token usage estimates, CNPJ mask validation and a provider-response test; it must pass CI before final review readiness.

## Security review
- Demo mode uses **fixed fictional** values; not OCR, not document extraction.
- Paid OpenAI path requires both an explicit API mode and environment opt-in. No provider keys are shipped, and no live calls run in CI.
- The app has no durable document storage, but Starlette may spool multipart uploads into OS temporary files. A bounded ASGI pre-parser checks full request sizes; provider-bound images are rebuilt from pixels to strip EXIF/GPS metadata. See `docs/privacy.md`.
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

## Codex findings remediation (2026-11-09)

The first explicitly authorized Codex Review of PR #1 reported six issues: upload pre-parser size checking (P1), metadata stripping, Decimal limits, reconciliation without subtotal, stale browser review response and financial validation metric (five P2). The implementation and regression tests were updated in the existing feature branch. The test suite now contains 61 passing tests, confirmed by [green GitHub Actions run 42741844565](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42741844565) with Ruff, mypy, README checks, regression evaluation, packaging and Docker. No additional paid AI call or main merge was made.

## Automatic follow-up Codex findings (2026-11-10)

Codex automatically reviewed commit `a0a53c6` and identified two additional P2 issues: alpha-channel image compositing and decimal-scale equivalence in evaluation scoring. Both received code and regression-test fixes; the 68-test intermediate version passed in [run 42823437181](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42823437181). The paid live provider remains untested by design.

## Follow-up Codex finding: stale usage (2026-11-10)

In the final Codex review of commit `d7441d4`, a P2 finding identified that a reused provider could carry forward earlier token usage when the latest response omitted or invalidated usage. The implementation resets `last_usage` for every request and rejects non-integer/negative token counts. Five provider-level regression cases and an offline live-evaluation metric test bring the suite to **74 passing cases**, verified in [green GitHub Actions run 42825215168](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42825215168). A related existing error-path test now also checks that stale usage is reset. This test never contacts a paid model.
