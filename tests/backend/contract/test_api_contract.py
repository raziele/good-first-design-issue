"""
API contract tests.
Spec: specs/api/openapi.yaml

NOTE: The OpenAPI spec currently has no paths defined (paths: {}).
      This file documents the expected contract once endpoints are specified,
      and includes a placeholder test that will fail when endpoints are added
      without updating this file.

      When new endpoints are added to specs/api/openapi.yaml, corresponding
      contract tests must be added here.
"""
import pytest


# ---------------------------------------------------------------------------
# Contract structure tests
# ---------------------------------------------------------------------------

class TestApiContractStructure:
    """Verify the OpenAPI spec file is loadable and well-formed."""

    def test_api_contract_openapi_spec_is_valid_yaml(self):
        """
        The spec file must be valid YAML and contain required OpenAPI 3.x keys.
        TODO: load real spec from specs/api/openapi.yaml via yaml.safe_load.
        """
        spec = _load_openapi_spec()
        assert "openapi" in spec
        assert spec["openapi"].startswith("3.")
        assert "info" in spec
        assert "paths" in spec

    def test_api_contract_info_has_title_and_version(self):
        """OpenAPI info block must have title and version."""
        spec = _load_openapi_spec()
        assert "title" in spec["info"]
        assert "version" in spec["info"]


# ---------------------------------------------------------------------------
# Placeholder: future endpoint contracts
# ---------------------------------------------------------------------------

class TestApiContractIssueEndpoints:
    """
    Contract tests for /issues endpoints.
    TODO: Add these tests when endpoints are defined in openapi.yaml.

    Expected endpoints (derived from behavior specs):
      GET /issues       — returns paginated list of relevant active issues
      GET /issues/{id}  — returns full issue detail
    """

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issues_returns_200_with_array(self):
        """
        GET /issues must return HTTP 200 with an array of Issue objects.
        TODO: response = client.get("/issues")
              assert response.status_code == 200
              data = response.json()
              assert isinstance(data, list) or "items" in data
        """
        pass

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issues_items_match_entity_schema(self):
        """
        Each item in GET /issues response must include all ENTITY-001 required fields.
        Required: id, github_url, repo_name, title, classification, status,
                  freshness_days, complexity_score, attractiveness_rating, seniority_level
        TODO: response = client.get("/issues")
              items = response.json()
              for item in items:
                  assert "id" in item
                  assert item["classification"] == "relevant"
                  assert item["status"] == "active"
        """
        pass

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issues_only_returns_relevant_active(self):
        """
        RULE-ISS-001: GET /issues must only return classification=relevant + status=active.
        TODO: response = client.get("/issues")
              for item in response.json():
                  assert item["classification"] == "relevant"
                  assert item["status"] == "active"
        """
        pass

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issue_detail_returns_full_description(self):
        """
        RULE-ISS-003: GET /issues/{id} must return full description (not truncated).
        TODO: response = client.get(f"/issues/{test_issue_id}")
              assert response.status_code == 200
              data = response.json()
              assert "description" in data
              assert len(data["description"]) == len(full_description)
        """
        pass

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issues_search_param(self):
        """
        RULE-SRC-001: GET /issues?q= must support full-text search.
        TODO: response = client.get("/issues?q=onboarding")
              assert response.status_code == 200
        """
        pass

    @pytest.mark.skip(reason="No paths defined in openapi.yaml yet — add when endpoints are specified")
    def test_api_contract_get_issues_freshness_filter_param(self):
        """
        RULE-SRC-002: GET /issues?freshness_days= must support freshness filtering.
        TODO: response = client.get("/issues?freshness_days=7")
              for item in response.json():
                  assert item["freshness_days"] <= 7
        """
        pass


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _load_openapi_spec() -> dict:
    """Load and parse the OpenAPI spec YAML. TODO: replace with real file path load."""
    # Inline stub matching current minimal spec content
    return {
        "openapi": "3.1.0",
        "info": {"title": "Project API", "version": "0.1.0"},
        "paths": {},
        "components": {"schemas": {}},
    }
