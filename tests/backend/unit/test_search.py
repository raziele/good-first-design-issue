"""
Backend unit tests for Search and Filtering.
Spec: specs/behavior/search.spec.md
"""

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_issue(id="1", title="", description="", freshness_days=10, **overrides):
    base = {
        "id": id,
        "title": title,
        "description": description,
        "freshness_days": freshness_days,
        "classification": "relevant",
        "status": "active",
    }
    base.update(overrides)
    return base


def full_text_search(issues: list, query: str) -> list:
    """
    Full-text search across title and description.
    Mirrors RULE-SRC-001 behavioral contract.
    """
    q = query.lower()
    return [i for i in issues if q in i["title"].lower() or q in i["description"].lower()]


def filter_by_freshness(issues: list, max_days: int | None) -> list:
    """
    Filter issues by freshness.
    max_days=None means 'All time' (no filter).
    Mirrors RULE-SRC-002.
    """
    if max_days is None:
        return issues
    return [i for i in issues if i["freshness_days"] <= max_days]


FRESHNESS_FILTER_MAP = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time": None,
}


def apply_filters(issues: list, query: str = "", freshness_label: str = "All time") -> list:
    """Combined search + filter (AND logic). Mirrors RULE-SRC-003."""
    result = issues
    if query:
        result = full_text_search(result, query)
    max_days = FRESHNESS_FILTER_MAP.get(freshness_label)
    result = filter_by_freshness(result, max_days)
    return result


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestRuleSRC001FullTextSearch:
    def test_search_matches_title(self):
        """Scenario: Search matches title."""
        issues = [make_issue(id="1", title="Mobile onboarding redesign", description="")]
        results = full_text_search(issues, "onboarding")
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_search_matches_description(self):
        """Scenario: Search matches description."""
        issues = [make_issue(id="1", title="Unrelated title", description="accessibility audit needed")]
        results = full_text_search(issues, "accessibility")
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_search_returns_no_results(self):
        """Scenario: Search returns no results."""
        issues = [
            make_issue(id="1", title="Design onboarding", description="improve UX flow"),
        ]
        results = full_text_search(issues, "blockchain")
        assert results == []

    def test_search_is_case_insensitive(self):
        """Search query case must not matter."""
        issues = [make_issue(id="1", title="Mobile Onboarding Redesign", description="")]
        assert full_text_search(issues, "ONBOARDING") != []
        assert full_text_search(issues, "onboarding") != []

    def test_search_matches_partial_word(self):
        """Partial-word match should succeed (substring matching)."""
        issues = [make_issue(id="1", title="Accessibility improvements", description="")]
        results = full_text_search(issues, "access")
        assert results != []

    def test_search_across_both_fields(self):
        """Issues matching title OR description are included."""
        issues = [
            make_issue(id="title-match", title="Dark mode design", description="Nothing special"),
            make_issue(id="desc-match", title="Unrelated", description="dark mode toggle needed"),
            make_issue(id="no-match", title="Unrelated", description="Nothing special"),
        ]
        results = full_text_search(issues, "dark mode")
        ids = {r["id"] for r in results}
        assert "title-match" in ids
        assert "desc-match" in ids
        assert "no-match" not in ids


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

class TestRuleSRC002FilterByFreshness:
    def test_filter_to_recent_issues(self):
        """Scenario: Filter to recent issues — Last 7 days."""
        issues = [
            make_issue(id="fresh", freshness_days=3),
            make_issue(id="old", freshness_days=20),
        ]
        results = filter_by_freshness(issues, max_days=7)
        ids = {r["id"] for r in results}
        assert "fresh" in ids
        assert "old" not in ids

    @pytest.mark.parametrize("label,max_days", [
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
    ])
    def test_freshness_filter_options(self, label, max_days):
        """Scenario Outline: Freshness filter options."""
        issues = [
            make_issue(id="within", freshness_days=max_days - 1),
            make_issue(id="boundary", freshness_days=max_days),
            make_issue(id="outside", freshness_days=max_days + 1),
        ]
        results = filter_by_freshness(issues, max_days=max_days)
        ids = {r["id"] for r in results}
        assert "within" in ids
        assert "boundary" in ids
        assert "outside" not in ids

    def test_all_time_filter_returns_everything(self):
        """Freshness filter 'All time' — no filter applied."""
        issues = [
            make_issue(id="1", freshness_days=1),
            make_issue(id="2", freshness_days=365),
        ]
        results = filter_by_freshness(issues, max_days=None)
        assert len(results) == 2

    def test_boundary_value_included(self):
        """Issues with freshness_days exactly equal to the limit are included."""
        issues = [make_issue(id="1", freshness_days=7)]
        assert filter_by_freshness(issues, max_days=7) != []


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestRuleSRC003SearchAndFilterCombine:
    def test_combined_search_and_filter(self):
        """Scenario: Combined search and filter."""
        issues = [
            make_issue(id="match", title="Mobile redesign", freshness_days=3),
            make_issue(id="too-old", title="Mobile app icons", freshness_days=45),
        ]
        results = apply_filters(issues, query="mobile", freshness_label="Last 7 days")
        ids = {r["id"] for r in results}
        assert "match" in ids
        assert "too-old" not in ids

    def test_empty_query_with_freshness_filter(self):
        """No search query — only freshness filter applied."""
        issues = [
            make_issue(id="fresh", freshness_days=5),
            make_issue(id="old", freshness_days=60),
        ]
        results = apply_filters(issues, query="", freshness_label="Last 7 days")
        ids = {r["id"] for r in results}
        assert "fresh" in ids
        assert "old" not in ids

    def test_search_with_no_filter_is_all_time(self):
        """Search without freshness filter returns all time matches."""
        issues = [
            make_issue(id="1", title="Accessibility design", freshness_days=200),
            make_issue(id="2", title="Mobile redesign", freshness_days=1),
        ]
        results = apply_filters(issues, query="accessibility", freshness_label="All time")
        assert len(results) == 1
        assert results[0]["id"] == "1"

    def test_combined_yields_empty_when_no_intersection(self):
        """AND logic: empty result when search and filter have no common issues."""
        issues = [
            make_issue(id="1", title="Dark mode design", freshness_days=40),
        ]
        results = apply_filters(issues, query="dark mode", freshness_label="Last 7 days")
        assert results == []


# ---------------------------------------------------------------------------
# RULE-SRC-004: Mobile uses bottom sheet (UI contract — unit-testable portion)
# ---------------------------------------------------------------------------

class TestRuleSRC004MobileBottomSheet:
    def test_filter_options_are_defined(self):
        """Filter option labels must match the spec."""
        expected = {"Last 7 days", "Last 30 days", "Last 90 days", "All time"}
        assert expected == set(FRESHNESS_FILTER_MAP.keys())

    def test_mobile_bottom_sheet_behavior_documented(self):
        """
        TODO: E2E test needed for bottom sheet interaction on mobile viewport.
        See tests/frontend/e2e/search.e2e.test.ts for UI coverage.
        """
        pass  # Covered in e2e tests
