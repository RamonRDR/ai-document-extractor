# Extraction schema v1

`FinancialDocument` includes nullable `document_type`, `issuer_name`, `issuer_cnpj`, `issue_date` (ISO YYYY-MM-DD), `document_number`, `currency` (three-letter code), `subtotal`, `discount`, `tax`, `surcharge`, `total`, plus `items` and `provenance`.

`Item` includes nullable `description`, `quantity`, `unit_price`, `total`.

Monetary amounts are JSON **strings** and parsed as `Decimal`, not binary floats. The parser accepts `1.234,56` and `1,234.56`; ambiguous formats may be rejected. Missing numeric values remain `null`; absent line items use `[]`.

Provenance: `extracted` means returned by the model (not guaranteed correct); `inferred` is reserved for explicitly inferred values and must be reviewed; `missing` means not identified; `demo` marks deterministic fictional example data. The OpenAI v1 prompt instructs the model not to infer. Live responses missing required structured-output fields are rejected; null fields are permitted. No verified field-level source citation or bounding boxes yet.

`ExtractionResult` returns `mode`, `document`, `issues`, `needs_review`, `processing_ms`, `prompt_version` and a clear `notice`. `ReviewResult` preserves original extraction and separate corrected record, confirmation and corrected validation issues.

Errors: unsupported MIME or magic → 415, invalid/corrupt document → 422, exceeded upload bound → 413, provider unavailable or malformed → 502, provider timeout → 504, live mode not enabled → 503, missing export confirmation → 409.
