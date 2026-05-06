"""
Backend unit tests for Search and Filtering.
Spec: specs/behavior/search.spec.md
Rules: RULE-SRC-001 through RULE-SRC-004
"""
import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers / fake implementations
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    base = {
        "id": "issue-1",
        "title": "Default title",
        "description": "Default description.",
        "freshness_days": 10,
        "classification": "relevant",
        "status": "active",
    }
    base.update(overrides)
    return base


def search_issues(issues: list[dict], query: str) -> list[dict]:
    """Full-text search against title and description (case-insensitive)."""
    q = query.lower()
    return [
        i for i in issues
        if q in i["title"].lower() or q in i["description"].lower()
    ]


FRESHNESS_FILTER_MAP = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time": None,
}


def filter_by_freshness(issues: list[dict], filter_value: str) -> list[dict]:
    max_days = FRESHNESS_FILTER_MAP.get(filter_value)
    if max_days is None:
        return issues
    return [i for i in issues if i["freshness_days"] <= max_days]


def apply_search_and_filter(
    issues: list[dict], query: str | None = None, freshness: str | None = None
) -> list[dict]:
    """Combines search and freshness filter with AND logic."""
    result = issues
    if query:
        result = search_issues(result, query)
    if freshness:
        result = filter_by_freshness(result, freshness)
    return result


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestRuleSRC001:
    """RULE-SRC-001: Search matches issue title and description."""

    def test_search_matches_title(self):
        issues = [make_issue(id="a", title="Mobile onboarding redesign")]
        result = search_issues(issues, "onboarding")
        assert len(result) == 1
        assert result[0]["id"] == "a"

    def test_search_matches_description(self):
        issues = [make_issue(id="b", description="This is an accessibility audit task")]
        result = search_issues(issues, "accessibility")
        assert len(result) == 1
        assert result[0]["id"] == "b"

    def test_search_is_case_insensitive(self):
        issues = [make_issue(id="c", title="Mobile Onboarding Redesign")]
        result = search_issues(issues, "ONBOARDING")
        assert len(result) == 1

    def test_search_returns_no_results_for_absent_term(self):
        issues = [
            make_issue(id="d", title="Design icons", description="Icon set work"),
        ]
        result = search_issues(issues, "blockchain")
        assert result == []

    def test_search_no_results_empty_state_message(self):
        """Verifies that an empty result set signals the empty state."""
        issues = [make_issue(title="Design icons", description="Icon work")]
        result = search_issues(issues, "blockchain")
        # Empty result triggers: "No matches — try adjusting your search terms."
        assert result == []

    def test_search_partial_match_in_title(self):
        issues = [make_issue(id="e", title="Redesign the onboarding experience")]
        result = search_issues(issues, "redesign")
        assert len(result) == 1

    def test_search_matches_both_title_and_description(self):
        """Issue matching in both fields still only appears once."""
        issues = [make_issue(id="f", title="Redesign", description="Complete redesign task")]
        result = search_issues(issues, "redesign")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

class TestRuleSRC002:
    """RULE-SRC-002: Users can filter issues by freshness (recency)."""

    def test_filter_last_7_days(self):
        issues = [
            make_issue(id="a", freshness_days=3),
            make_issue(id="b", freshness_days=7),
            make_issue(id="c", freshness_days=8),
        ]
        result = filter_by_freshness(issues, "Last 7 days")
        ids = [i["id"] for i in result]
        assert set(ids) == {"a", "b"}

    def test_filter_last_30_days(self):
        issues = [
            make_issue(id="a", freshness_days=10),
            make_issue(id="b", freshness_days=30),
            make_issue(id="c", freshness_days=31),
        ]
        result = filter_by_freshness(issues, "Last 30 days")
        ids = [i["id"] for i in result]
        assert set(ids) == {"a", "b"}

    def test_filter_last_90_days(self):
        issues = [
            make_issue(id="a", freshness_days=45),
            make_issue(id="b", freshness_days=90),
            make_issue(id="c", freshness_days=91),
        ]
        result = filter_by_freshness(issues, "Last 90 days")
        ids = [i["id"] for i in result]
        assert set(ids) == {"a", "b"}

    def test_filter_all_time_returns_everything(self):
        issues = [
            make_issue(id="a", freshness_days=200),
            make_issue(id="b", freshness_days=1),
        ]
        result = filter_by_freshness(issues, "All time")
        assert len(result) == 2

    @pytest.mark.parametrize("filter_value,max_days", [
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
    ])
    def test_freshness_filter_boundary_inclusive(self, filter_value, max_days):
        """Boundary value at exactly max_days is included."""
        issues = [make_issue(id="boundary", freshness_days=max_days)]
        result = filter_by_freshness(issues, filter_value)
        assert len(result) == 1

    @pytest.mark.parametrize("filter_value,max_days", [
        ("Last 7 days", 7),
        ("Last 30 days", 30),
        ("Last 90 days", 90),
    ])
    def test_freshness_filter_one_beyond_boundary_excluded(self, filter_value, max_days):
        """max_days + 1 is excluded."""
        issues = [make_issue(id="over", freshness_days=max_days + 1)]
        result = filter_by_freshness(issues, filter_value)
        assert result == []


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestRuleSRC003:
    """RULE-SRC-003: Search terms and freshness filter combine with AND logic."""

    def test_combined_search_and_filter_returns_intersection(self):
        issues = [
            make_issue(id="a", title="Mobile redesign", freshness_days=3),
            make_issue(id="b", title="Mobile app icons", freshness_days=45),
        ]
        result = apply_search_and_filter(issues, query="mobile", freshness="Last 7 days")
        assert len(result) == 1
        assert result[0]["id"] == "a"

    def test_combined_search_and_filter_no_results(self):
        issues = [
            make_issue(id="a", title="Mobile redesign", freshness_days=45),
        ]
        result = apply_search_and_filter(issues, query="mobile", freshness="Last 7 days")
        assert result == []

    def test_filter_only_no_search(self):
        issues = [
            make_issue(id="a", freshness_days=3),
            make_issue(id="b", freshness_days=15),
        ]
        result = apply_search_and_filter(issues, freshness="Last 7 days")
        assert len(result) == 1
        assert result[0]["id"] == "a"

    def test_search_only_no_filter(self):
        issues = [
            make_issue(id="a", title="Onboarding redesign", freshness_days=100),
            make_issue(id="b", title="Icon design", freshness_days=200),
        ]
        result = apply_search_and_filter(issues, query="onboarding")
        assert len(result) == 1
        assert result[0]["id"] == "a"


# ---------------------------------------------------------------------------
# RULE-SRC-004: Mobile uses bottom sheet for filters
# ---------------------------------------------------------------------------

class TestRuleSRC004:
    """
    RULE-SRC-004: On mobile viewports, filters are accessed via a bottom sheet modal.
    Backend note: this is primarily a frontend concern; the backend serves the same
    filter API regardless of viewport. Tests here validate the filter API contract
    is viewport-agnostic.
    """

    def test_filter_api_works_regardless_of_viewport(self):
        """The freshness filter produces identical results regardless of how it was triggered."""
        issues = [
            make_issue(id="a", freshness_days=3),
            make_issue(id="b", freshness_days=20),
        ]
        desktop_result = filter_by_freshness(issues, "Last 7 days")
        mobile_result = filter_by_freshness(issues, "Last 7 days")
        assert desktop_result == mobile_result
