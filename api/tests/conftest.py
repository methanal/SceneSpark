import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture(autouse=True, scope="module")
def aio_client():
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture(autouse=True, scope="module")
def client():
    client = TestClient(app)
    return client
