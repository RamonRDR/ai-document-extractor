# ADR 0001: Stateless demo, provider boundary and PDF renderer

**Status:** Accepted (2026-11-07)

**Context.** A portfolio project needs reproducible public CI, a real multimodal integration, and a clear MIT-licensed application. An AGPL PDF dependency would complicate licensing and redistribution of a networked app.

**Decision.** Use Python 3.14, FastAPI/Pydantic v2, Pillow, and the permissively licensed `pypdfium2` for single-page PDF rasterization. Use an extraction provider protocol with a fixed synthetic demo implementation and a strictly opt-in OpenAI adapter. Keep no persistent records or local files. Require human confirmation before exports.

**Consequences.** CI runs free and deterministic. Live extraction incurs provider cost and privacy transfer only after explicit opt-in. The demo is not an OCR system. One-page limit, no auth, no storage and no background worker are deliberately documented scope boundaries.

**Alternative considered.** PyMuPDF is technically suitable and supports Python 3.14, but its AGPL/commercial licensing warrants an explicit compatibility assessment for MIT distribution. `pypdfium2` avoids this licensing concern for the demo.
