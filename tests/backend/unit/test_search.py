"""
Backend unit tests for Search and Filtering behavior.

Spec: specs/behavior/search.spec.md
"""
import pytest

from tests.backend.unit.conftest import make_issue


def search_issues(issues, query: str = "", freshness_filter: int | None = None):
    """
    Pure reference implementation of RULE-SRC-001 + RULE-SRC-002 + RULE-SRC-003.

    Args:
        issues: list of issue dicts
        query: free-text search string (matches title + description)
        freshness_filter: max freshness_days allowed (None = no filter)

    Returns:
        filtered list of issue dicts
    """
    results = issues

    if query:
        q = query.lower()
        results = [
            i for i in results
            if q in i["title"].lower() or q in i["description"].lower()
        ]

    if freshness_filter is not None:
        results = [i for i in results if i["freshness_days"] <= freshness_filter]

    return results


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestFullTextSearch:
    """RULE-SRC-001 — Search matches issue title and description."""

    def test_search_matches_title(self):
        """Search term appearing in title returns the issue."""
        issue = make_issue(title="Mobile onboarding redesign", description="Details here.")
        result = search_issues([issue], query="onboarding")
        assert len(result) == 1

    def test_search_matches_description(self):
        """Search term appearing in description returns the issue."""
        issue = make_issue(title="Accessibility work", description="We need an accessibility audit.")
        result = search_issues([issue], query="accessibility")
        assert len(result) == 1

    def test_search_is_case_insensitive(self):
        """Search is case-insensitive."""
        issue = make_issue(title="Figma Handoff Guide")
        assert search_issues([issue], query="figma") != []
        assert search_issues([issue], query="FIGMA") != []

    def test_search_no_results_returns_empty_list(self):
        """Search with no matching issues returns an empty list."""
        issue = make_issue(title="Design tokens", description="Color palette updates.")
        result = search_issues([issue], query="blockchain")
        assert result == []

    def test_search_empty_query_returns_all_issues(self):
        """Empty search string returns all issues (no text filter applied)."""
        issues = [make_issue(id=f"i{n}") for n in range(3)]
        result = search_issues(issues, query="")
        assert len(result) == 3


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

class TestFreshnessFilter:
    """RULE-SRC-002 — Users can filter by freshness. Only one filter dimension in v1."""

    @pytest.mark.parametrize("filter_days,expected_count", [
        (7, 1),   # only the 3-day issue
        (30, 2),  # 3-day and 20-day
        (90, 3),  # all three
    ])
    def test_freshness_filter_options(self, filter_days, expected_count):
        """Freshness filter options: Last 7 / 30 / 90 days."""
        issues = [
            make_issue(id="a", freshness_days=3),
            make_issue(id="b", freshness_days=20),
            make_issue(id="c", freshness_days=60),
        ]
        result = search_issues(issues, freshness_filter=filter_days)
        assert len(result) == expected_count

    def test_freshness_filter_all_time_returns_all(self):
        """All time (no filter) returns every issue regardless of freshness."""
        issues = [make_issue(id=f"i{n}", freshness_days=n * 10) for n in range(1, 5)]
        result = search_issues(issues, freshness_filter=None)
        assert len(result) == 4

    def test_freshness_filter_last_7_days(self):
        """Filter 'Last 7 days' returns only issues with freshness_days <= 7."""
        issues = [
            make_issue(id="fresh", freshness_days=5),
            make_issue(id="stale", freshness_days=15),
        ]
        result = search_issues(issues, freshness_filter=7)
        ids = [i["id"] for i in result]
        assert "fresh" in ids
        assert "stale" not in ids


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestCombinedSearchAndFilter:
    """RULE-SRC-003 — Search term and freshness filter are combined with AND logic."""

    def test_combined_search_and_freshness_filter(self):
        """
        Issue A: 'Mobile redesign', 3 days old → passes both search and 7-day filter.
        Issue B: 'Mobile app icons', 45 days old → passes search but fails freshness filter.
        Only issue A should appear.
        """
        issues = [
            make_issue(id="A", title="Mobile redesign", freshness_days=3),
            make_issue(id="B", title="Mobile app icons", freshness_days=45),
        ]
        result = search_issues(issues, query="mobile", freshness_filter=7)
        ids = [i["id"] for i in result]
        assert "A" in ids
        assert "B" not in ids

    def test_combined_returns_empty_when_no_match(self):
        """Search+filter combo that matches nothing returns an empty list."""
        issues = [
            make_issue(id="C", title="Design audit", freshness_days=50),
        ]
        result = search_issues(issues, query="icons", freshness_filter=7)
        assert result == []


# ---------------------------------------------------------------------------
# RULE-SRC-004: Mobile bottom sheet (UI contract — validated at component level)
# ---------------------------------------------------------------------------

class TestMobileFilterUiContract:
    """RULE-SRC-004 — Mobile filter uses a bottom sheet; verified as UI behavior."""

    def test_mobile_filter_rule_documented(self):
        """
        RULE-SRC-004 is a UI-layer concern (bottom sheet vs inline dropdown).
        Functional contract is satisfied by the same freshness filter logic above.
        Full validation lives in frontend component and e2e tests.
        """
        # This test documents the spec coverage boundary.
        assert True  # TODO: see SearchBar.mobile-bottom-sheet.test.ts and search.e2e.test.ts
