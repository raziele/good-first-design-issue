"""
Shared fixtures for backend tests.
All issue data is constructed as plain dicts matching ENTITY-001 (domain-model.md).
"""

import pytest
from datetime import datetime, timezone, timedelta


def make_issue(**overrides):
    """
    Factory for creating test Issue dicts conforming to ENTITY-001.
    Caller overrides any field needed for the specific scenario.
    """
    base = {
        "id": "test-iss-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 100,
        "title": "Redesign the settings page",
        "description": "We need a full UX redesign with wireframes and Figma mockups.",
        "labels": [],
        "has_media": False,
        "created_at": datetime.now(timezone.utc) - timedelta(days=5),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
        "freshness_days": 5,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


@pytest.fixture
def relevant_active_issue():
    return make_issue(classification="relevant", status="active")


@pytest.fixture
def not_relevant_issue():
    return make_issue(classification="not_relevant", status="active")


@pytest.fixture
def archived_issue():
    return make_issue(classification="relevant", status="archived")


@pytest.fixture
def claimed_design_issue():
    return make_issue(
        classification="relevant",
        status="active",
        is_claimed=True,
    )


@pytest.fixture
def old_issue():
    """Issue created 100 days ago — should be excluded on initial fetch."""
    return make_issue(
        created_at=datetime.now(timezone.utc) - timedelta(days=100),
        freshness_days=100,
    )


@pytest.fixture
def recent_issue():
    """Issue created 30 days ago — should be included on initial fetch."""
    return make_issue(
        created_at=datetime.now(timezone.utc) - timedelta(days=30),
        freshness_days=30,
    )
