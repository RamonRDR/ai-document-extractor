# Privacy and threat model

- **Use only synthetic or suitably anonymized documents in public repositories and public demos.** A public demo without authentication must never be exposed with private documents.
- Default `demo` mode is a **fixed fictional record**, not OCR or AI extraction. Passing a real document does not cause its contents to be read by a model in demo mode.
- The live `openai` mode is disabled unless `ALLOW_PAID_AI=1` and `OPENAI_API_KEY` are both provided. If enabled, the request sends the rendered document image to the provider; understand its privacy terms first.
- There are no file or result persistence paths. Logs should include neither full documents nor secrets. Do not log HTTP request bodies or provider payloads at a reverse proxy.
- Magic-byte validation, MIME agreement checks, one-page PDF restriction, a default 5 MiB upload bound, 12-megapixel image bound and at most five batch files reduce common abuse risks.
- PDF parsing remains native-code input processing. For untrusted production traffic, deploy a sandboxed worker with CPU, memory and wall-time limits, malware scanning, authentication and rate limits. These are **not implemented** in v1.
- Extracted document text is untrusted. The system prompt tells the model to ignore embedded instructions. This is mitigation, not a proof of injection resistance.
- CSV escapes spreadsheet-formula prefixes. The UI and API are stateless; users must verify field correctness before export.
- We do not automatically execute paid evaluation, and CI has no provider secrets or paid calls.
