"""
Shared fixtures for Level8 backend tests.
All fixtures are hermetic — no live network calls, no live database.
"""
import pytest
from datetime import datetime, timezone


def make_issue(**overrides):
    """Factory for Issue domain objects matching ENTITY-001."""
    base = {
        "id": "issue-001",
        "github_url": "https://github.com/org/repo/issues/1",
        "repo_name": "org/repo",
        "repo_stars": 1200,
        "title": "Create wireframes for settings page",
        "description": "Design the settings page layout. Include mockup, user flow, Figma link.",
        "description_truncated": "Design the settings page layout. Include mockup, user flow, Figma link."[:200],
        "labels": ["design", "good first issue"],
        "has_media": False,
        "created_at": datetime(2026, 4, 10, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 15, tzinfo=timezone.utc),
        "freshness_days": 26,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2026, 5, 6, tzinfo=timezone.utc),
    }
    base.update(overrides)
    return base


@pytest.fixture
def relevant_active_issue():
    return make_issue()


@pytest.fixture
def not_relevant_issue():
    return make_issue(
        id="issue-002",
        title="Fix API endpoint for user auth",
        description="database migration, REST API changes needed.",
        classification="not_relevant",
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
        description="See screenshot: ![screenshot](https://example.com/img.png)",
        has_media=True,
    )


@pytest.fixture
def issue_no_media():
    return make_issue(
        id="issue-006",
        description="Plain text description with no media links.",
        has_media=False,
    )
