"""Shared fixtures for backend tests."""
import pytest
from datetime import datetime, timezone


def make_issue(**overrides):
    """Factory for Issue domain objects."""
    defaults = {
        "id": "issue-001",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 500,
        "title": "Create wireframes for settings page",
        "description": "We need mockup, user flow, and Figma designs for the new settings page.",
        "description_truncated": "We need mockup, user flow, and Figma designs for the new settings page.",
        "labels": ["design", "good first issue"],
        "has_media": False,
        "created_at": datetime(2026, 4, 20, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 21, tzinfo=timezone.utc),
        "freshness_days": 16,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2026, 5, 6, tzinfo=timezone.utc),
    }
    return {**defaults, **overrides}


@pytest.fixture
def relevant_active_issue():
    return make_issue()


@pytest.fixture
def not_relevant_issue():
    return make_issue(
        id="issue-002",
        classification="not_relevant",
        title="Fix API endpoint for user auth",
        description="database, migration, REST API",
    )


@pytest.fixture
def archived_issue():
    return make_issue(id="issue-003", status="archived")


@pytest.fixture
def claimed_issue():
    return make_issue(id="issue-004", is_claimed=True)


@pytest.fixture
def issue_with_media():
    return make_issue(
        id="issue-005",
        has_media=True,
        description="See screenshot: ![screenshot](https://example.com/img.png)",
    )


@pytest.fixture
def issue_list(relevant_active_issue, not_relevant_issue, archived_issue, claimed_issue):
    return [relevant_active_issue, not_relevant_issue, archived_issue, claimed_issue]
