"""Tests for RULE-CLS-001..004: Issue classification logic."""

from __future__ import annotations

import pytest

from app.classification import classify_issue


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------


def test_design_issue_classified_as_relevant():
    """RULE-CLS-001 / Scenario: Design issue is classified as relevant."""
    result = classify_issue(
        title="Create wireframes for settings page",
        description="We need mockup, user flow, and Figma designs for the settings page.",
    )
    assert result == "relevant"


def test_backend_issue_classified_as_not_relevant():
    """RULE-CLS-001 / Scenario: Backend issue is classified as not relevant."""
    result = classify_issue(
        title="Fix API endpoint for user auth",
        description="The database migration breaks the REST API handler.",
    )
    assert result == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------


def test_empty_description_is_not_relevant():
    """RULE-CLS-002 / Scenario: Empty description."""
    result = classify_issue(
        title="Some issue",
        description="",
    )
    assert result == "not_relevant"


def test_placeholder_only_description_is_not_relevant():
    """RULE-CLS-002 / Scenario: Placeholder-only description."""
    result = classify_issue(
        title="Some issue",
        description="## Description\n## TODO\n## Acceptance Criteria",
    )
    assert result == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "title,description",
    [
        ("Add test coverage for auth", "We need unit test and QA case coverage."),
        ("New API endpoint for users", "Create a backend database migration."),
        ("Refactor auth module", "Rename X to Y and refactor existing code."),
        ("Implement in code", "code base for the new feature."),
        ("Update sprite sheet", "Add UTF files and new game assets."),
    ],
)
def test_exclusion_patterns_classify_as_not_relevant(title: str, description: str):
    """RULE-CLS-004 / Scenario Outline: Exclusion by category."""
    result = classify_issue(title=title, description=description)
    assert result == "not_relevant"
