<div align="center">

# AI Document Extractor 📄

**Extrae datos estructurados de documentos financieros, verifica los importes y exporta con revisión humana.**

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

![pytest 68 passing](https://img.shields.io/badge/pytest-68%20passing-0A9EDC)
![pytest-asyncio](https://img.shields.io/badge/pytest--asyncio-enabled-0A9EDC)
![Ruff lint and format](https://img.shields.io/badge/Ruff-lint%20%26%20format-D7FF64)
![mypy type checked](https://img.shields.io/badge/mypy-type%20checked-2A6DB4)
![OpenAPI documented](https://img.shields.io/badge/OpenAPI-%2Fdocs%20validated-6BA539)
![30 synthetic fixtures](https://img.shields.io/badge/Synthetic%20Evaluation-30%20fixtures-607D8B)
![Package build](https://img.shields.io/badge/Package%20Build-wheel%20%2B%20sdist-455A64)
[![Feature branch formatting](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml/badge.svg?branch=feat%2Fdocument-extractor-full-implementation)](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/format-branch.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation)

<!-- BADGES:END -->

</div>

> **Estado del proyecto:** implementación en el [PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1), con los seis hallazgos iniciales de Codex corregidos en la rama; pendiente de revisión adicional y autorización de merge. El [CI de la rama de desarrollo](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation) está en verde. Sin despliegue ni paquete publicado.

## Descripción general

API sin almacenamiento persistente para documentos financieros de una página, con revisión humana. Recibe PDF, PNG o JPEG, estructura campos financieros, verifica coherencia aritmética y exige confirmación antes de exportar CSV/JSON. Demuestra backend Python, automatización financiera, contratos REST tipados, adaptadores multimodales y CI alojado para un portafolio internacional.

**Dos modos distintos:** `demo` devuelve **siempre el mismo registro ficticio** para cada archivo válido; **no** realiza OCR ni extracción por IA. `openai` es un adaptador multimodal **opcional** implementado; la extracción real de pago **no se ha ejecutado ni evaluado**.

## Funcionalidades implementadas

- PDF, PNG y JPEG de una sola página; validación de firma/MIME, tamaño de carga, renderizado PDF, integridad de imagen y límites de píxeles.
- Interfaz sustituible de proveedor, demostración determinista ficticia y adaptador multimodal opcional de OpenAI con salida JSON Schema estructurada.
- Contratos Pydantic v2 con valores nulos, procedencia (`extracted`, `inferred`, `missing` o `demo`), tiempo y advertencias.
- CNPJ brasileño, fechas, importes `Decimal`, líneas, subtotales, descuentos, impuestos y recargos.
- Interfaz web para corrección y confirmación; resultado original separado del corregido.
- Exportación CSV y JSON solo después de confirmar; protección del CSV contra fórmulas.
- Lotes de hasta cinco archivos de forma predeterminada, errores individuales y contadores.
- 30 documentos sintéticos, pruebas simuladas del proveedor, comprobación de paquetes y automatización GitHub Actions.

## Tecnologías

| Capa | Implementación real |
| --- | --- |
| Ejecución | **Python 3.14**, paquete versión `0.1.0` |
| API y datos | FastAPI **0.128+** (mínimo declarado), Pydantic **v2** (2.11+), Uvicorn ASGI, python-multipart **0.0.20+** |
| Documentos y HTTP | pypdfium2 **5.14+** para PDF, Pillow **11.3+** para imágenes, httpx **0.28+** para peticiones al proveedor |
| Límite de IA | Adaptador OpenAI API con imágenes multimodales y JSON Schema estricto, desactivado inicialmente; extracción externa real sin validar |
| Calidad | pytest, pytest-asyncio, Ruff lint/formato, mypy estricto, 30 casos deterministas de evaluación sintética |
| Automatización | GitHub Actions, wheel/sdist con Hatchling, build Docker, formato de ramas de funcionalidades |

Las versiones con `+` son **mínimos declarados**, no versiones exactas fijadas. El manifiesto admite versiones compatibles posteriores. No se utiliza base de datos, Redis, Alembic, Docker Compose, RAG, embeddings ni MCP.

## Arquitectura

Flujo: **carga → validación → preparación PDF/imagen → proveedor elegido → contrato Pydantic → comprobaciones financieras → corrección humana → exportación confirmada**. Sin base de datos ni almacenamiento documental. Consulta el [diagrama](docs/architecture.md), los [schemas](docs/schema.md) y la [ADR del proveedor/renderizador](docs/adr/0001-provider-and-renderer.md).

## Requisitos

Python **3.14** y pip. Docker Engine es opcional. No hace falta clave de IA para demostración, pruebas o CI. No utilices documentos privados en demos públicas.

## Instalación

~~~bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
~~~

En Windows, activa con `.venv\Scripts\activate`. Build opcional del contenedor: `docker build -t ai-document-extractor .`.

## Configuración

Consulta [`.env.example`](.env.example). Es una referencia: la aplicación lee **variables de entorno**, no carga este archivo automáticamente.

| Variable | Finalidad |
| --- | --- |
| `ALLOW_PAID_AI` | Predeterminado `0`; debe ser `1` para modo real |
| `OPENAI_API_KEY` | Secreto para extracción real autorizada; nunca publicarlo |
| `AI_MODEL` | Predeterminado `gpt-4o-mini` (configuración, no validación real) |
| `AI_TIMEOUT_SECONDS` | Tiempo máximo del proveedor (20 segundos) |
| `MAX_UPLOAD_BYTES` | Límite por archivo (5.242.880 bytes) |
| `MAX_BATCH_FILES` | Límite de archivos por petición (5) |
| `EVAL_LIVE` | Activación adicional para evaluación real manual, `0` |
| `AI_INPUT_USD_PER_MILLION` / `AI_OUTPUT_USD_PER_MILLION` | Tarifas proporcionadas para una **estimación**, no límite de facturación |

El CI no usa secretos. La extracción real puede generar costes y envía la imagen del documento al proveedor.

## Ejecución e interfaz

~~~bash
uvicorn document_extractor.api:app --reload
# Alternativa Docker:
docker run --rm -p 8000:8000 ai-document-extractor
~~~

La interfaz local está en `http://127.0.0.1:8000/`. Endpoints REST:

| Endpoint | Función |
| --- | --- |
| `GET /health` | Estado básico |
| `GET /docs` | Swagger UI y documentación automática de FastAPI |
| `GET /openapi.json` | Schema OpenAPI |
| `POST /api/v1/extract` | Un archivo, `mode=demo` o `mode=openai` |
| `POST /api/v1/batch` | Varios archivos con resultados independientes |
| `POST /api/v1/review` | Registro original, campos corregidos y confirmación |
| `POST /api/v1/export/csv` / `POST /api/v1/export/json` | Descarga de datos revisados y confirmados |

## Ejemplo de uso

~~~bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@recibo-ficticio.png;type=image/png" \
  -F "mode=demo"
~~~

Respuesta abreviada **ficticia**, no extraída del archivo:

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

La respuesta completa incluye moneda, número, subtotal/ajustes, procedencia, advertencias y tiempo. [Detalles del schema](docs/schema.md).

## Validaciones financieras y revisión humana

Formato y dígitos de CNPJ, fechas, importes, cantidades, productos de línea y conciliación de subtotal/ajustes producen advertencias, sin reescribir silenciosamente valores. Los campos ausentes quedan nulos. Envía `{"original": <resultado-extracción>, "corrected": <documento-editado>, "confirmed": true}` a `POST /api/v1/review` y luego su respuesta a `/api/v1/export/csv` o `/api/v1/export/json`. Sin confirmación devuelve **HTTP 409**. La interfaz web ofrece este flujo.

## Procesamiento por lotes

Envía varios campos multipart `files` a `POST /api/v1/batch`; cada elemento devuelve índice, éxito, resultado o error. Los contadores separan éxitos y fallos. Límite inicial de cinco archivos y tamaño individual limitado.

## Pruebas automatizadas y evaluación

~~~bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture --report evaluation-report.json
python -m build
~~~

La suite incluye ahora **68 casos de prueba**. El [workflow de CI](https://github.com/RamonRDR/ai-document-extractor/actions/workflows/ci.yml?query=branch%3Afeat%2Fdocument-extractor-full-implementation) ejecuta las pruebas y valida automáticamente la cifra del badge con el informe JUnit. La [ejecución anterior de 61 pruebas](https://github.com/RamonRDR/ai-document-extractor/actions/runs/42741844565) precede las correcciones adicionales. Las 30 fixtures ficticias prueban documentos, schemas y reglas, pero **no** miden precisión real de IA ni costes reales. La evaluación de pago es manual y requiere `EVAL_LIVE=1`, `ALLOW_PAID_AI=1`, clave y presupuesto positivo. Solo con un **presupuesto ya autorizado**, el comando es `python -m evaluation.runner --mode live --max-documents 3 --max-usd-per-document 0.20 --budget-usd 0.60`. Es una reserva estimada, **no** un bloqueo de facturación real.

## GitHub Actions y mantenimiento de badges

El [workflow de CI](.github/workflows/ci.yml) ejecuta Ruff, formato, mypy, pytest, revisión de schema, fixtures, build wheel/sdist y Docker por separado. El [formateador de ramas](.github/workflows/format-branch.yml) solo puede modificar ramas `feat/**`, nunca `main`. CI usa runners alojados y **nunca invoca modelos de pago**.

El **badge pytest es estático y verificable**: [`scripts/check_readme_badges.py`](scripts/check_readme_badges.py) compara la cifra con el JUnit XML real y revisa los tres README. Cambiar pruebas obliga a actualizar los tres y superar CI. Los badges de CI/formato apuntan a la rama de desarrollo hasta que PR #1 se integre; después deben apuntar a `main`. [Inventario de badges](docs/badges.md).

## Seguridad y privacidad

El documento es entrada no confiable; su texto jamás se ejecuta como comando. Comprobaciones de formato/MIME, páginas, bytes/píxeles, timeout y prevención de fórmulas CSV reducen el riesgo. La aplicación no guarda documentos de forma permanente, pero el parser multipart de Starlette puede usar archivos temporales del sistema operativo. Un middleware limita el tamaño total antes del parser; se eliminan los metadatos EXIF/GPS de las imágenes enviadas al proveedor. No hay secretos, documentos financieros reales, llamadas pagadas ni publicación incluidos. Revisa el [modelo de amenazas y privacidad](docs/privacy.md).

## Limitaciones conocidas y futuras mejoras

Solo una página; sin autenticación, límite global de peticiones, antivirus, aislamiento del parser PDF, persistencia, multi-tenancy, colas ni recuadros de evidencia por campo. No hay benchmark real del modelo opcional; toda extracción requiere verificación humana. Para producción harían falta aislamiento, acceso controlado y evaluación real. Este proyecto **no está desplegado** como plataforma contable.

## Estructura del repositorio

| Ruta | Responsabilidad |
| --- | --- |
| `src/document_extractor/api.py` / `ui.html` | HTTP e interfaz de revisión |
| `src/document_extractor/documents.py` | Validación y renderizado PDF/imagen |
| `src/document_extractor/providers.py` / `prompts.py` | Proveedores, JSON Schema y prompt |
| `src/document_extractor/schemas.py` / `validation.py` / `finance.py` | Campos y reglas financieras |
| `evaluation/` / `tests/` | Evaluación sintética y pruebas |
| `scripts/check_readme_badges.py` | Consistencia de README frente a JUnit |
| `.github/workflows/` | CI y formateador de ramas |
| `docs/` | Arquitectura, schemas, ADR, privacidad y auditorías |

## Contribuciones

Abre issue o PR describiendo la propuesta; mantén pruebas y tres idiomas sincronizados. Ejecuta Ruff, mypy y pytest. No subas documentos personales, claves ni secretos. El [PR #1](https://github.com/RamonRDR/ai-document-extractor/pull/1) ya recibió la revisión inicial de Codex y corrigió sus seis hallazgos; espera nueva comprobación y autorización de merge.

## Licencia

Código de aplicación bajo [licencia MIT](LICENSE), copyright 2026 Ramon Rodriguez. Las dependencias tienen sus propias licencias, incluido PDFium/pypdfium2. No se garantiza soporte comercial ni seguridad en producción.
