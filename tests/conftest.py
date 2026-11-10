"""Only synthetic in-memory fixtures."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from document_extractor.api import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def png() -> bytes:
    image = Image.new("RGB", (140, 100), "white")
    buffer = BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()


@pytest.fixture
def jpeg() -> bytes:
    image = Image.new("RGB", (140, 100), "white")
    buffer = BytesIO()
    image.save(buffer, "JPEG")
    return buffer.getvalue()


@pytest.fixture
def png_with_bad_idat_crc(png: bytes) -> bytes:
    """A valid PNG whose IDAT CRC has been intentionally corrupted."""
    data = bytearray(png)
    marker = data.find(b"IDAT")
    assert marker > 12
    chunk_size = int.from_bytes(data[marker - 4 : marker], "big")
    crc_offset = marker + 4 + chunk_size
    assert crc_offset + 4 <= len(data)
    data[crc_offset] ^= 1
    return bytes(data)
