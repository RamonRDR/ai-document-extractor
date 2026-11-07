"""Validate magic bytes and decode a single-page document without disk I/O."""

from dataclasses import dataclass
from io import BytesIO

import pymupdf
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_PIXELS = 12_000_000
MAX_RENDER_PIXELS = 12_000_000
MAX_DIMENSION = 2048
Image.MAX_IMAGE_PIXELS = MAX_IMAGE_PIXELS


class DocumentError(ValueError):
    def __init__(self, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class PreparedDocument:
    image: bytes
    mime_type: str


def prepare_document(data: bytes, content_type: str | None, max_bytes: int) -> PreparedDocument:
    if len(data) > max_bytes:
        raise DocumentError("Upload exceeds configured size limit", 413)
    if not data:
        raise DocumentError("Empty document")
    if data.startswith(b"%PDF-"):
        detected = "application/pdf"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        detected = "image/png"
    elif data.startswith(b"\xff\xd8\xff"):
        detected = "image/jpeg"
    else:
        raise DocumentError("Only valid PDF, PNG and JPEG documents are supported", 415)
    if content_type and content_type not in ("application/octet-stream", detected):
        raise DocumentError("Declared content type does not match file content", 415)

    if detected == "application/pdf":
        try:
            with pymupdf.open(stream=data, filetype="pdf") as doc:
                if doc.needs_pass:
                    raise DocumentError("Encrypted PDFs are not supported")
                if doc.page_count != 1:
                    raise DocumentError("Only single-page PDFs are supported")
                page = doc.load_page(0)
                rect = page.rect
                if rect.width <= 0 or rect.height <= 0:
                    raise DocumentError("Invalid PDF dimensions")
                scale = min(1.6, (MAX_RENDER_PIXELS / (rect.width * rect.height)) ** 0.5)
                if scale <= 0:
                    raise DocumentError("Invalid PDF rendering scale")
                pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
                image_data = pixmap.tobytes("png")
        except DocumentError:
            raise
        except Exception as exc:
            raise DocumentError("Unreadable or corrupt PDF") from exc
    else:
        image_data = data
    try:
        with Image.open(BytesIO(image_data)) as image:
            if getattr(image, "n_frames", 1) != 1:
                raise DocumentError("Animated or multipage images are not supported")
            image.verify()
        with Image.open(BytesIO(image_data)) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise DocumentError("Image pixel limit exceeded", 413)
            normalized = ImageOps.exif_transpose(image).convert("RGB")
            normalized.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
            buffer = BytesIO()
            normalized.save(buffer, format="PNG")
            safe_image = buffer.getvalue()
    except DocumentError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise DocumentError("Unreadable or corrupt image") from exc
    if len(safe_image) > 15 * 1024 * 1024:
        raise DocumentError("Prepared image exceeds processing limit", 413)
    return PreparedDocument(image=safe_image, mime_type="image/png")
