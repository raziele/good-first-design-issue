"""Shared fixtures for backend tests."""
import pytest
from datetime import datetime, timezone


def _make_issue(**overrides):
    """Return a minimal Issue-shaped dict. Overrides replace defaults."""
    base = {
        "id": "github_1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 100,
        "title": "Design the settings page",
        "description": "Create wireframes for the settings page, including user flow and Figma mockups.",
        "labels": [],
        "has_media": False,
        "created_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "freshness_days": 5,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2026, 5, 1, tzinfo=timezone.utc),
    }
    base.update(overrides)
    return base


@pytest.fixture
def relevant_active_issue():
    return _make_issue()


@pytest.fixture
def not_relevant_issue():
    return _make_issue(
        id="github_2",
        title="Fix API endpoint for user auth",
        description="The REST API endpoint for authentication is broken. Needs database migration.",
        classification="not_relevant",
    )


@pytest.fixture
def archived_issue():
    return _make_issue(
        id="github_3",
        status="archived",
    )


@pytest.fixture
def claimed_relevant_issue():
    return _make_issue(
        id="github_4",
        is_claimed=True,
    )


@pytest.fixture
def design_issue_raw():
    """Raw GitHub API-shaped issue dict (pre-classification)."""
    return {
        "id": "github_5",
        "title": "Create wireframes for settings page",
        "body": "We need mockups for the settings page. Please provide user flow and Figma designs.",
        "html_url": "https://github.com/owner/repo/issues/5",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [],
    }


@pytest.fixture
def backend_issue_raw():
    """Raw GitHub API-shaped issue dict for a backend/non-design task."""
    return {
        "id": "github_6",
        "title": "Fix API endpoint for user auth",
        "body": "The REST API endpoint is failing. Needs database migration and backend fixes.",
        "html_url": "https://github.com/owner/repo/issues/6",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [],
    }
