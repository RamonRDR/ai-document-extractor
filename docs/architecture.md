# Architecture

```mermaid
flowchart LR
  Browser[Browser review UI] --> API[FastAPI]
  API --> Guard[Magic bytes / page limit / Pillow]
  Guard --> Raster[pypdfium2 PDF rasterization]
  Raster --> Router{Provider}
  Router --> Demo[Fixed synthetic demo]
  Router --> Live[Opt-in OpenAI multimodal API]
  Demo --> Contract[Pydantic strict schema]
  Live --> Contract
  Contract --> Validation[CNPJ / Decimal / cross-checks]
  Validation --> Human[Human correction and confirmation]
  Human --> Export[JSON / CSV escaping]
```

No database, queue, background tasks or durable document storage. A bounded request-body middleware validates full multipart size before parsing; Starlette may spool upload parts to OS temporary disk. Provider-bound images are rebuilt from pixels to drop EXIF/GPS metadata. Live mode explicitly sends the normalized image bytes to an external provider.

Modules: `documents` for bounded input/rasterization; `providers` for replaceable extraction; `schemas` for strict contracts and provenance; `validation` for financial checks; `service` for orchestration; `api` for HTTP/UI/export; `evaluation` for synthetic fixtures.

This is a demonstration, not an accounting system. There is no authentication, persistence, job queue, tenant isolation or production-grade anti-abuse layer.
