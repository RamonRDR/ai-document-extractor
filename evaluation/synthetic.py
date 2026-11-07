"""Generate synthetic receipts in three formats and multiple visual layouts."""

from dataclasses import dataclass
from decimal import Decimal
from io import BytesIO

from PIL import Image, ImageDraw

from document_extractor.schemas import FinancialDocument


@dataclass(frozen=True)
class Case:
    index: int
    format: str
    layout: str
    expected: FinancialDocument


def cases() -> list[Case]:
    layouts = ("compact", "wide", "dense", "header-left", "centered")
    result: list[Case] = []
    for index in range(30):
        amount = Decimal("10") + index
        expected = FinancialDocument(
            document_type=("receipt", "invoice", "service_receipt")[index % 3],
            issuer_name=f"FICTIONAL SHOP {index + 1:02d}",
            issuer_cnpj=None,
            issue_date="2026-01-15",
            document_number=f"EXAMPLE-{index + 1:03d}",
            currency="BRL" if index % 2 == 0 else "USD",
            subtotal=amount,
            total=amount,
            items=[
                {"description": "Test item", "quantity": "1", "unit_price": amount, "total": amount}
            ],
        )
        result.append(Case(index, ("png", "jpeg", "pdf")[index % 3], layouts[index % 5], expected))
    return result


def _pdf(lines: list[str]) -> bytes:
    """Make a valid one-page Helvetica PDF using only synthetic ASCII text."""
    commands = ["BT /F1 12 Tf 50 760 Td 16 TL"]
    for line in lines:
        escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        commands.append(f"({escaped}) Tj T*")
    commands.append("ET")
    stream = "\n".join(commands).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Count 1 /Kids [3 0 R] >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(content))
        content.extend(f"{i} 0 obj\n".encode() + obj + b"\nendobj\n")
    pointer = len(content)
    content.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        content.extend(f"{offset:010d} 00000 n \n".encode())
    content.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{pointer}\n%%EOF\n".encode()
    )
    return bytes(content)


def render(case: Case) -> bytes:
    doc = case.expected
    lines = [
        f"FICTIONAL DATA / layout: {case.layout}",
        f"Issuer: {doc.issuer_name}",
        f"Document: {doc.document_number}",
        f"Issue date: {doc.issue_date}",
        f"Type: {doc.document_type}",
        f"Currency: {doc.currency}",
        "Test item x 1",
        f"TOTAL: {doc.total}",
    ]
    if case.layout in ("wide", "centered"):
        lines.insert(1, "=======================================")
    if case.layout == "dense":
        lines.extend(["SYNTHETIC SAMPLE - NOT AN ACTUAL INVOICE"] * 2)
    if case.format == "pdf":
        return _pdf(lines)
    image = Image.new("RGB", (1100, 650), "white")
    draw = ImageDraw.Draw(image)
    x = 80 if case.layout != "centered" else 270
    gap = 40 if case.layout != "dense" else 26
    for i, line in enumerate(lines):
        draw.text((x, 40 + i * gap), line, fill="black")
    buffer = BytesIO()
    image.save(buffer, format="JPEG" if case.format == "jpeg" else "PNG")
    return buffer.getvalue()
