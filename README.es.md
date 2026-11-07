# AI Document Extractor

[English](README.md) · [Português](README.pt-BR.md) · **Español**

API Python sin almacenamiento para extraer datos financieros estructurados de documentos de una página, comprobar importes y permitir revisión humana. Muestra FastAPI, IA multimodal, Pydantic, Decimal, automatización y CI.

> **Importante:** el modo de demostración devuelve siempre un registro fijo y ficticio, con independencia del archivo. **No ejecuta OCR ni extracción real mediante IA.** El modo real necesita habilitación explícita y puede generar costes. No subas información privada a una demo pública.

## Funciones

Carga de PDF, PNG y JPEG con detección de firma, coincidencia MIME, límite de tamaño, píxeles y página única; interfaz de revisión en `/` y OpenAPI en `/docs`; proveedores intercambiables `demo` y `openai`; JSON estructurado con valores nulos, procedencia y alertas. Exportación CSV/JSON tras confirmación y lotes de hasta cinco documentos con errores aislados.

## Tecnologías y arquitectura

Python 3.14, FastAPI, Pydantic v2, httpx, Pillow, pypdfium2, pytest, Ruff, mypy, Docker y GitHub Actions. Separación entre validación de entradas, renderizado PDF, proveedor de IA, schema, comprobaciones financieras, revisión y exportación. Ver [diagrama](docs/architecture.md), [schemas](docs/schema.md) y [decisión técnica](docs/adr/0001-provider-and-renderer.md).

## Instalación

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn document_extractor.api:app --reload
```

En Windows: `.venv\Scripts\activate`. Abre `http://127.0.0.1:8000/` o `/docs`. Docker: `docker build -t ai-document-extractor .` y `docker run --rm -p 8000:8000 ai-document-extractor`.

## Configuración y ejemplo de carga

Consulta [`.env.example`](.env.example). La demo funciona sin claves. Una llamada real autorizada requiere `ALLOW_PAID_AI=1` y `OPENAI_API_KEY`; manda `mode=openai`. No publiques credenciales ni habilites modelos de pago en CI.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/extract \
  -F "file=@recibo-ficticio.png;type=image/png" -F "mode=demo"
```

Fragmento del JSON **ficticio**, no extraído del archivo:

```json
{"mode":"demo","document":{"issuer_name":"Example Studio (FICTIONAL)","total":"140.00","issuer_cnpj":null},"needs_review":true}
```

El resultado completo también contiene tipo, fecha, número, moneda, subtotal, descuento, impuestos, recargos, partidas, procedencia, problemas y tiempo. Los importes se representan mediante `Decimal`.

## Comprobaciones financieras y revisión humana

CNPJ con dígitos de control, fechas, cantidades positivas, sumas por partida, subtotales y ajustes. Campos no detectados siguen nulos. Envía `original`, `corrected` y `confirmed: true` a `POST /api/v1/review` y después el resultado a `/api/v1/export/csv` o `/api/v1/export/json`. Sin confirmación se devuelve HTTP 409. Se preservan por separado el resultado original y el corregido.

## Pruebas, evaluación y GitHub Actions

```bash
ruff check .
ruff format --check .
mypy --ignore-missing-imports src/document_extractor
pytest -q
python -m evaluation.runner --mode fixture
```

30 documentos completamente sintéticos permiten verificar formatos, layouts y reglas. Esta evaluación determinista **no mide precisión real de IA**, por lo que dicha métrica es nula. La evaluación con proveedor real es optativa, manual y exige configuración de presupuesto; no limita la factura del proveedor. GitHub Actions comprueba Ruff, formato, tipos, pruebas, regresión sintética, paquete y Docker en infraestructura alojada. Sin ejecución en la máquina personal ni llamadas de pago.

## Seguridad, límites y licencia

Sin archivos persistentes y sin credenciales en el código. Los textos del documento se tratan como datos no confiables, los archivos se limitan y el CSV evita inyección de fórmulas. Aún no hay autenticación, escaneo antimalware, aislamiento del parser, límites globales, base de datos, varias páginas ni referencias visuales por campo. No lo uses en producción sin controles adicionales. Consulta [privacidad](docs/privacy.md). Código de aplicación con licencia [MIT](LICENSE); dependencias con licencias propias.
