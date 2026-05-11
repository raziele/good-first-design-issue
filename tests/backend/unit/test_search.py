"""Tests for search and filtering rules: RULE-SRC-001, RULE-SRC-002, RULE-SRC-003."""

from __future__ import annotations

import pytest

from app.search import search_and_filter_issues


# ---------------------------------------------------------------------------
# Shared fixture helper
# ---------------------------------------------------------------------------


def _issue(
    *,
    id: str = "1",
    title: str = "Issue title",
    description: str = "Issue description",
    freshness_days: int = 5,
) -> dict:
    return {
        "id": id,
        "title": title,
        "description": description,
        "freshness_days": freshness_days,
    }


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------


def test_search_matches_title():
    """RULE-SRC-001 / Scenario: Search matches title."""
    issues = [_issue(id="1", title="Mobile onboarding redesign")]
    result = search_and_filter_issues(issues, query="onboarding")
    assert any(i["id"] == "1" for i in result)


def test_search_matches_description():
    """RULE-SRC-001 / Scenario: Search matches description."""
    issues = [_issue(id="1", description="We need an accessibility audit for the login page.")]
    result = search_and_filter_issues(issues, query="accessibility")
    assert any(i["id"] == "1" for i in result)


def test_search_returns_empty_when_no_match():
    """RULE-SRC-001 / Scenario: Search returns no results."""
    issues = [_issue(id="1", title="Mobile redesign", description="Some description")]
    result = search_and_filter_issues(issues, query="blockchain")
    assert result == []


def test_search_is_case_insensitive():
    """RULE-SRC-001 / Search should be case-insensitive."""
    issues = [_issue(id="1", title="Mobile Onboarding Redesign")]
    result = search_and_filter_issues(issues, query="ONBOARDING")
    assert any(i["id"] == "1" for i in result)


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filter_value,max_days",
    [
        ("last_7_days", 7),
        ("last_30_days", 30),
        ("last_90_days", 90),
    ],
)
def test_freshness_filter_keeps_issues_within_window(filter_value: str, max_days: int):
    """RULE-SRC-002 / Scenario Outline: Freshness filter options."""
    issues = [
        _issue(id="within", freshness_days=max_days),
        _issue(id="outside", freshness_days=max_days + 1),
    ]
    result = search_and_filter_issues(issues, freshness_filter=filter_value)
    ids = [i["id"] for i in result]
    assert "within" in ids
    assert "outside" not in ids


def test_all_time_filter_returns_all_issues():
    """RULE-SRC-002 / 'All time' filter applies no freshness constraint."""
    issues = [
        _issue(id="1", freshness_days=5),
        _issue(id="2", freshness_days=200),
    ]
    result = search_and_filter_issues(issues, freshness_filter="all_time")
    assert len(result) == 2


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------


def test_combined_search_and_freshness_filter():
    """RULE-SRC-003 / Scenario: Combined search and filter."""
    issues = [
        _issue(id="recent_match", title="Mobile redesign", freshness_days=3),
        _issue(id="old_match", title="Mobile app icons", freshness_days=45),
        _issue(id="recent_no_match", title="Totally unrelated", freshness_days=1),
    ]
    result = search_and_filter_issues(
        issues, query="mobile", freshness_filter="last_7_days"
    )
    ids = [i["id"] for i in result]
    assert ids == ["recent_match"]
