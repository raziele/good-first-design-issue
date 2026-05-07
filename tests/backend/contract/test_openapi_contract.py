"""
API contract tests.
Spec: specs/api/openapi.yaml

The openapi.yaml is currently at v0.1.0 with empty paths.
These tests validate the contract skeleton and will expand as endpoints are added.
"""

import pytest
import yaml
from pathlib import Path


OPENAPI_PATH = Path(__file__).parents[4] / "specs" / "api" / "openapi.yaml"


@pytest.fixture(scope="module")
def openapi_spec():
    with open(OPENAPI_PATH) as f:
        return yaml.safe_load(f)


class TestOpenAPIContractStructure:
    def test_spec_file_exists(self):
        """openapi.yaml must exist in specs/api/."""
        assert OPENAPI_PATH.exists(), "specs/api/openapi.yaml not found"

    def test_openapi_version_field_present(self, openapi_spec):
        """Spec must declare openapi version."""
        assert "openapi" in openapi_spec

    def test_openapi_version_is_3x(self, openapi_spec):
        """Spec must use OpenAPI 3.x."""
        assert openapi_spec["openapi"].startswith("3.")

    def test_info_block_present(self, openapi_spec):
        """Spec must have an info block."""
        assert "info" in openapi_spec

    def test_info_title_present(self, openapi_spec):
        """info.title must be present."""
        assert "title" in openapi_spec["info"]
        assert openapi_spec["info"]["title"] != ""

    def test_info_version_present(self, openapi_spec):
        """info.version must be present."""
        assert "version" in openapi_spec["info"]

    def test_paths_block_present(self, openapi_spec):
        """Spec must have a paths block (may be empty at v0.1.0)."""
        assert "paths" in openapi_spec

    def test_components_block_present(self, openapi_spec):
        """Spec must have a components block."""
        assert "components" in openapi_spec


class TestOpenAPIHealthEndpointContract:
    """
    TODO: Add contract test for GET /health once endpoint is declared in openapi.yaml.
    Expected contract:
      - path: /health
      - method: GET
      - response 200: { status: string, version: string }
    """

    def test_health_endpoint_contract_todo(self, openapi_spec):
        """
        TODO: /health path not yet declared in openapi.yaml.
        Once added, assert:
          assert "/health" in openapi_spec["paths"]
          assert "get" in openapi_spec["paths"]["/health"]
        """
        pass  # TODO: add /health to openapi.yaml and expand this test


class TestOpenAPIIssueEndpointsContract:
    """
    TODO: Contract tests for Issue endpoints (GET /issues, GET /issues/{id}).
    Expected schema fields per domain-model.md ENTITY-001:
      id, github_url, repo_name, repo_stars, title, description_truncated,
      labels, has_media, freshness_days, classification, is_claimed,
      complexity_score, attractiveness_rating, seniority_level, status
    """

    def test_issues_list_endpoint_contract_todo(self, openapi_spec):
        """
        TODO: GET /issues endpoint not yet declared in openapi.yaml.
        Spec reference: specs/behavior/issues.spec.md RULE-ISS-001
        """
        pass  # TODO

    def test_issue_detail_endpoint_contract_todo(self, openapi_spec):
        """
        TODO: GET /issues/{id} endpoint not yet declared in openapi.yaml.
        Spec reference: specs/behavior/issues.spec.md RULE-ISS-003
        """
        pass  # TODO
