"""
Contract tests for the Level8 backend API.
Specs: specs/api/openapi.yaml, src/backend/app/main.py

Uses FastAPI's built-in TestClient (sync ASGI wrapper) — no live server needed.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# /health endpoint
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self):
        response = client.get("/health")
        assert response.headers["content-type"].startswith("application/json")

    def test_health_body_has_status_ok(self):
        response = client.get("/health")
        body = response.json()
        assert body["status"] == "ok"

    def test_health_body_has_version(self):
        response = client.get("/health")
        body = response.json()
        assert "version" in body
        assert isinstance(body["version"], str)
        assert len(body["version"]) > 0
