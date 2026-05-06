"""
Tests for Search and Filtering behavior.
Spec: specs/behavior/search.spec.md
"""
from datetime import datetime, timedelta, timezone
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(id="issue-1", title="Design issue", description="Some design content",
               freshness_days=10, classification="relevant", status="active", **overrides):
    return {
        "id": id,
        "title": title,
        "description": description,
        "freshness_days": freshness_days,
        "classification": classification,
        "status": status,
        **overrides,
    }


ISSUE_STORE = [
    make_issue(id="1", title="Mobile onboarding redesign", description="Redesign the mobile onboarding flow", freshness_days=3),
    make_issue(id="2", title="Settings page layout", description="Improve accessibility audit for settings", freshness_days=20),
    make_issue(id="3", title="Icon system overhaul", description="Update the icon library for consistency", freshness_days=60),
    make_issue(id="4", title="Mobile app icons", description="New icon set for mobile platforms", freshness_days=45),
]


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestSearchFullText:
    """RULE-SRC-001: Search matches title and description fields."""

    def test_search_full_text_matches_title(self):
        """
        Scenario: Search matches title
        Given an issue with title "Mobile onboarding redesign"
        When a user searches for "onboarding"
        Then the issue appears in search results
        """
        results = _search(ISSUE_STORE, query="onboarding")
        ids = [i["id"] for i in results]
        assert "1" in ids

    def test_search_full_text_matches_description(self):
        """
        Scenario: Search matches description
        Given an issue with description containing "accessibility audit"
        When a user searches for "accessibility"
        Then the issue appears in search results
        """
        results = _search(ISSUE_STORE, query="accessibility")
        ids = [i["id"] for i in results]
        assert "2" in ids

    def test_search_full_text_returns_empty_state_for_no_match(self):
        """
        Scenario: Search returns no results
        Given no issues contain the word "blockchain"
        When a user searches for "blockchain"
        Then an empty result set is returned
        """
        results = _search(ISSUE_STORE, query="blockchain")
        assert results == [], "Search for absent term must return empty list"

    def test_search_full_text_case_insensitive(self):
        """Search must be case-insensitive."""
        results_lower = _search(ISSUE_STORE, query="mobile")
        results_upper = _search(ISSUE_STORE, query="MOBILE")
        assert len(results_lower) == len(results_upper)

    def test_search_full_text_short_query_no_results(self):
        """
        Edge case from search.flow.md: query < 2 chars → no search executed.
        """
        results = _search(ISSUE_STORE, query="a")
        assert results == [], "Single-character query must return no results"

    def test_search_full_text_special_characters_escaped(self):
        """
        Edge case: special characters in query → search proceeds normally (no crash).
        """
        try:
            results = _search(ISSUE_STORE, query="mobile & icons | test (design)")
            assert isinstance(results, list)
        except Exception as exc:
            pytest.fail(f"Search with special characters raised: {exc}")


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

class TestSearchFreshnessFilter:
    """RULE-SRC-002: Freshness filter restricts by freshness_days threshold."""

    def test_search_freshness_filter_last_7_days(self):
        """
        Scenario: Filter to recent issues
        Given issues with various freshness values
        When a user applies a "Last 7 days" freshness filter
        Then only issues with freshness_days <= 7 are shown
        """
        results = _filter_by_freshness(ISSUE_STORE, max_days=7)
        for issue in results:
            assert issue["freshness_days"] <= 7

    @pytest.mark.parametrize("filter_label,max_days", [
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
    ])
    def test_search_freshness_filter_options(self, filter_label, max_days):
        """
        Scenario Outline: Freshness filter options
        Given multiple issues with varying freshness
        When a user selects freshness filter {filter_value}
        Then only issues matching the criteria are shown
        """
        results = _filter_by_freshness(ISSUE_STORE, max_days=max_days)
        for issue in results:
            assert issue["freshness_days"] <= max_days, (
                f"Filter '{filter_label}' must exclude issues older than {max_days} days"
            )

    def test_search_freshness_filter_all_time_returns_all(self):
        """
        Scenario Outline: "All time" filter applies no restriction.
        """
        results = _filter_by_freshness(ISSUE_STORE, max_days=None)
        assert len(results) == len(ISSUE_STORE)

    def test_search_freshness_filter_boundary_inclusive(self):
        """Issue with freshness_days exactly equal to threshold must be included."""
        issues = [make_issue(id="x", freshness_days=7)]
        results = _filter_by_freshness(issues, max_days=7)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestSearchCombined:
    """RULE-SRC-003: Search and freshness filter combine with AND logic."""

    def test_search_combined_search_and_filter(self):
        """
        Scenario: Combined search and filter
        Given an issue titled "Mobile redesign" created 3 days ago
        And an issue titled "Mobile app icons" created 45 days ago
        When a user searches "mobile" and filters to "Last 7 days"
        Then only "Mobile redesign" appears in results
        """
        issues = [
            make_issue(id="recent", title="Mobile redesign", description="Redesign mobile flow", freshness_days=3),
            make_issue(id="old", title="Mobile app icons", description="New icon set", freshness_days=45),
        ]
        results = _search_and_filter(issues, query="mobile", max_days=7)
        ids = [i["id"] for i in results]
        assert "recent" in ids
        assert "old" not in ids

    def test_search_combined_no_results_when_filter_eliminates_match(self):
        """Search matches but freshness filter removes all → empty result."""
        issues = [make_issue(id="old", title="accessibility audit", freshness_days=60)]
        results = _search_and_filter(issues, query="accessibility", max_days=7)
        assert results == []

    def test_search_combined_empty_query_with_filter(self):
        """Empty search + freshness filter should apply freshness filter only."""
        results = _search_and_filter(ISSUE_STORE, query="", max_days=7)
        for issue in results:
            assert issue["freshness_days"] <= 7


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _search(issues: list, query: str) -> list:
    """
    Full-text search across title + description.
    TODO: replace with real backend search implementation.
    """
    if len(query.strip()) < 2:
        return []
    import re
    # Escape special regex chars so search proceeds normally (RULE-SRC-001 edge case)
    safe_query = re.escape(query.strip())
    pattern = re.compile(safe_query, re.IGNORECASE)
    return [
        i for i in issues
        if pattern.search(i.get("title", "")) or pattern.search(i.get("description", ""))
    ]


def _filter_by_freshness(issues: list, max_days) -> list:
    """
    Apply freshness filter.
    max_days=None means "All time" — no filter applied.
    TODO: replace with real backend filter implementation.
    """
    if max_days is None:
        return list(issues)
    return [i for i in issues if i["freshness_days"] <= max_days]


def _search_and_filter(issues: list, query: str, max_days) -> list:
    """
    Combined AND search + freshness filter.
    TODO: replace with real backend implementation.
    """
    after_filter = _filter_by_freshness(issues, max_days)
    if not query.strip():
        return after_filter
    return _search(after_filter, query)
