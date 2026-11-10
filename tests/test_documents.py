"""Hardened single-page PDF and image upload parsing."""

import pytest

from document_extractor.documents import DocumentError, prepare_document
from evaluation.synthetic import cases, render


@pytest.mark.parametrize("index", [0, 1, 2, 5, 8])
def test_synthetic_formats(index: int) -> None:
    case = cases()[index]
    raw = render(case)
    content_type = {"png": "image/png", "jpeg": "image/jpeg", "pdf": "application/pdf"}[case.format]
    prepared = prepare_document(raw, content_type, 5_242_880)
    assert prepared.image.startswith(b"\x89PNG")
    assert prepared.mime_type == "image/png"


@pytest.mark.parametrize(
    ("raw", "mime", "code"),
    [
        (b"", "image/png", 422),
        (b"not an image", "image/png", 415),
        (b"%PDF-FAKE", "application/pdf", 422),
        (b"\x89PNG\r\n\x1a\nBROKEN", "image/png", 422),
        (b"\xff\xd8\xffNOT_JPEG", "image/jpeg", 422),
    ],
)
def test_bad_documents(raw: bytes, mime: str, code: int) -> None:
    with pytest.raises(DocumentError) as exc:
        prepare_document(raw, mime, 5_242_880)
    assert exc.value.status_code == code


def test_declared_mime_mismatch(png: bytes) -> None:
    with pytest.raises(DocumentError) as exc:
        prepare_document(png, "application/pdf", 5_242_880)
    assert exc.value.status_code == 415


def test_upload_limit(png: bytes) -> None:
    with pytest.raises(DocumentError) as exc:
        prepare_document(png, "image/png", 10)
    assert exc.value.status_code == 413


def test_image_metadata_is_stripped_before_provider_payload() -> None:
    from io import BytesIO

    from PIL import Image

    exif_marker = "PRIVATE_GPS_REFERENCE_123456789"
    picture = Image.new("RGB", (100, 75), "white")
    exif = Image.Exif()
    exif[270] = exif_marker  # ImageDescription
    stream = BytesIO()
    picture.save(stream, "JPEG", exif=exif)
    assert exif_marker.encode() in stream.getvalue()
    rendered = prepare_document(stream.getvalue(), "image/jpeg", 5_242_880)
    assert exif_marker.encode() not in rendered.image
    with Image.open(BytesIO(rendered.image)) as normalized:
        assert normalized.getexif().get(270) is None
        assert normalized.size == (100, 75)


@pytest.mark.parametrize("image_mode", ["RGBA", "LA", "P"])
def test_transparent_document_is_composited_on_white(image_mode: str) -> None:
    """Black content must stay legible against originally transparent pixels."""
    from io import BytesIO

    from PIL import Image

    if image_mode == "RGBA":
        image = Image.new("RGBA", (32, 24), (0, 0, 0, 0))
        image.putpixel((10, 8), (0, 0, 0, 255))
    elif image_mode == "LA":
        image = Image.new("LA", (32, 24), (0, 0))
        image.putpixel((10, 8), (0, 255))
    else:
        image = Image.new("P", (32, 24), 0)
        image.putpalette([0, 0, 0] * 256)
        image.info["transparency"] = 0
        image.putpixel((10, 8), 1)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    prepared = prepare_document(buffer.getvalue(), "image/png", 5_242_880)
    with Image.open(BytesIO(prepared.image)) as result:
        assert result.mode == "RGB"
        assert result.getpixel((0, 0)) == (255, 255, 255)
        assert result.getpixel((10, 8)) == (0, 0, 0)
