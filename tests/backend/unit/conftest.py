"""Shared fixtures for backend unit tests."""
import pytest
from datetime import datetime, timezone


def make_issue(**overrides):
    """Factory for Issue domain objects (plain dicts matching ENTITY-001)."""
    defaults = {
        "id": "issue-001",
        "github_url": "https://github.com/org/repo/issues/1",
        "repo_name": "org/repo",
        "repo_stars": 1200,
        "title": "Design new onboarding flow",
        "description": "We need a full UX redesign of the onboarding. Figma mockups welcome.",
        "description_truncated": "We need a full UX redesign of the onboarding. Figma mockups welcome.",
        "labels": ["design", "ux"],
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
def active_relevant_issue():
    return make_issue()


@pytest.fixture
def archived_issue():
    return make_issue(status="archived", classification="relevant")


@pytest.fixture
def not_relevant_issue():
    return make_issue(classification="not_relevant")


@pytest.fixture
def claimed_issue():
    return make_issue(is_claimed=True)


@pytest.fixture
def issue_with_media():
    return make_issue(
        has_media=True,
        description="See screenshot: ![screenshot](https://example.com/img.png)",
    )


@pytest.fixture
def issue_no_media():
    return make_issue(has_media=False, description="Plain text description only.")
