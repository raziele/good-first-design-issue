"""
Backend integration tests for the FastAPI application.
Covers the /health endpoint confirmed in src/backend/app/main.py.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        """GET /health must return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """GET /health body must contain status=ok."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_returns_version(self, client):
        """GET /health body must include a version field."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_health_content_type_is_json(self, client):
        """GET /health must return application/json."""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
