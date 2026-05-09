"""
Shared fixtures for backend tests.
"""
import pytest


@pytest.fixture
def sample_design_issue():
    return {
        "id": "gh-001",
        "title": "Create wireframes for settings page",
        "description": "We need a mockup, user flow, and Figma file.",
        "classification": "relevant",
        "status": "active",
        "freshness_days": 5,
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.8,
        "seniority_level": "junior",
        "has_media": False,
        "repo_name": "org/project",
        "repo_stars": 1500,
        "github_url": "https://github.com/org/project/issues/1",
    }


@pytest.fixture
def sample_not_relevant_issue():
    return {
        "id": "gh-002",
        "title": "Fix API endpoint for user auth",
        "description": "Update the database migration and REST API handler.",
        "classification": "not_relevant",
        "status": "active",
        "freshness_days": 3,
        "is_claimed": False,
        "complexity_score": "high",
        "attractiveness_rating": 0.1,
        "seniority_level": "senior",
        "has_media": False,
        "repo_name": "org/backend",
        "repo_stars": 200,
        "github_url": "https://github.com/org/backend/issues/2",
    }
