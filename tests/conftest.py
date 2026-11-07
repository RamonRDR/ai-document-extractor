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
