"""Stateless FastAPI interface for extraction, review and controlled export."""

import csv
import io
import json
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response

from .documents import DocumentError
from .providers import ProviderError
from .schemas import BatchEntry, BatchResult, ExtractionResult, ReviewRequest, ReviewResult
from .service import extract_document
from .settings import Settings
from .validation import validate_financial

app = FastAPI(
    title="AI Document Extractor",
    version="0.1.0",
    description="One-page financial extraction with transparent demo mode and human review.",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def interface() -> str:
    return Path(__file__).with_name("ui.html").read_text(encoding="utf-8")


async def _extract(upload: UploadFile, mode: Literal["demo", "openai"], settings: Settings) -> ExtractionResult:
    try:
        raw = await upload.read(settings.max_upload_bytes + 1)
        return await extract_document(raw, upload.content_type, mode, settings)
    except (DocumentError, ProviderError) as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    finally:
        await upload.close()


@app.post("/api/v1/extract", response_model=ExtractionResult)
async def extract(
    file: Annotated[UploadFile, File(description="PDF, PNG or JPEG, maximum 5 MB by default")],
    mode: Annotated[Literal["demo", "openai"], Form()] = "demo",
) -> ExtractionResult:
    return await _extract(file, mode, Settings.from_env())


@app.post("/api/v1/batch", response_model=BatchResult)
async def batch(
    files: Annotated[list[UploadFile], File(description="1 to 5 documents by default")],
    mode: Annotated[Literal["demo", "openai"], Form()] = "demo",
) -> BatchResult:
    settings = Settings.from_env()
    if not 1 <= len(files) <= settings.max_batch_files:
        raise HTTPException(status_code=413, detail="Too many documents in batch")
    entries: list[BatchEntry] = []
    for index, uploaded in enumerate(files):
        try:
            result = await _extract(uploaded, mode, settings)
            entries.append(BatchEntry(index=index, success=True, result=result))
        except HTTPException as exc:
            entries.append(BatchEntry(index=index, success=False, error=str(exc.detail)))
    count = sum(entry.success for entry in entries)
    return BatchResult(entries=entries, success_count=count, failure_count=len(entries) - count)


@app.post("/api/v1/review", response_model=ReviewResult)
async def review(request: ReviewRequest) -> ReviewResult:
    issues = validate_financial(request.corrected)
    return ReviewResult(
        original=request.original,
        corrected=request.corrected,
        confirmed=request.confirmed,
        issues=issues,
    )


def _require_confirmed(reviewed: ReviewResult) -> None:
    if not reviewed.confirmed:
        raise HTTPException(status_code=409, detail="Human confirmation required before export")


@app.post("/api/v1/export/json")
async def export_json(reviewed: ReviewResult) -> Response:
    _require_confirmed(reviewed)
    payload = json.dumps(reviewed.model_dump(mode="json"), ensure_ascii=False, indent=2)
    return Response(
        payload,
        media_type="application/json",
        headers={"Content-Disposition": 'attachment; filename="reviewed-document.json"'},
    )


def _csv_safe(value: object) -> str:
    text = "" if value is None else str(value)
    if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + text
    return text


@app.post("/api/v1/export/csv")
async def export_csv(reviewed: ReviewResult) -> Response:
    _require_confirmed(reviewed)
    doc = reviewed.corrected
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["document_type", "issuer_name", "issuer_cnpj", "issue_date", "document_number", "currency", "total", "item_description", "item_quantity", "item_unit_price", "item_total"])
    for item in doc.items or [None]:
        values = [
            doc.document_type, doc.issuer_name, doc.issuer_cnpj, doc.issue_date,
            doc.document_number, doc.currency, doc.total,
            item.description if item else None,
            item.quantity if item else None,
            item.unit_price if item else None,
            item.total if item else None,
        ]
        writer.writerow([_csv_safe(value) for value in values])
    return Response(
        output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="reviewed-document.csv"'},
    )
