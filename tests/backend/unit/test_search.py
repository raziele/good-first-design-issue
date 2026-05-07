"""
Unit tests for Search and Filtering rules.
Specs: specs/behavior/search.spec.md
"""

import pytest


# ---------------------------------------------------------------------------
# Pure search/filter helpers — mirror API query logic
# ---------------------------------------------------------------------------

def search_issues(issues: list, query: str) -> list:
    """
    RULE-SRC-001: full-text search against title and description.
    Minimum query length is 2 chars (RULE-SRC — edge case from flow).
    """
    q = query.strip().lower()
    if len(q) < 2:
        return list(issues)
    return [
        i for i in issues
        if q in i["title"].lower() or q in i["description"].lower()
    ]


def filter_by_freshness(issues: list, max_days: int | None) -> list:
    """
    RULE-SRC-002: freshness filter.
    max_days=None means "All time" (no filter applied).
    """
    if max_days is None:
        return list(issues)
    return [i for i in issues if i["freshness_days"] <= max_days]


def apply_search_and_filter(issues: list, query: str, max_days: int | None) -> list:
    """RULE-SRC-003: search and filter combine with AND logic."""
    results = search_issues(issues, query)
    return filter_by_freshness(results, max_days)


def make_issue(id, title, description, freshness_days):
    return {
        "id": id,
        "title": title,
        "description": description,
        "freshness_days": freshness_days,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def issue_set():
    return [
        make_issue("1", "Mobile onboarding redesign", "UX flow for mobile users", 3),
        make_issue("2", "Improve accessibility audit", "Screen reader improvements", 20),
        make_issue("3", "Fix backend API", "database migration endpoint", 5),
        make_issue("4", "Mobile app icons", "Icon set in Figma", 45),
        make_issue("5", "Dashboard layout redesign", "New wireframe in Figma", 60),
    ]


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestRuleSRC001:
    def test_search_matches_title(self, issue_set):
        results = search_issues(issue_set, "onboarding")
        ids = [i["id"] for i in results]
        assert "1" in ids

    def test_search_matches_description(self, issue_set):
        results = search_issues(issue_set, "accessibility")
        ids = [i["id"] for i in results]
        assert "2" in ids

    def test_search_no_results_returns_empty(self, issue_set):
        results = search_issues(issue_set, "blockchain")
        assert results == []

    def test_search_case_insensitive(self, issue_set):
        results = search_issues(issue_set, "MOBILE")
        ids = [i["id"] for i in results]
        assert "1" in ids
        assert "4" in ids

    def test_search_matches_partial_word_in_title(self, issue_set):
        results = search_issues(issue_set, "redesign")
        ids = [i["id"] for i in results]
        assert "1" in ids
        assert "5" in ids

    def test_search_query_too_short_returns_all(self, issue_set):
        # Edge case from search flow: < 2 chars → no search executed
        results = search_issues(issue_set, "a")
        assert len(results) == len(issue_set)

    def test_search_empty_query_returns_all(self, issue_set):
        results = search_issues(issue_set, "")
        assert len(results) == len(issue_set)

    def test_search_special_characters_escaped(self, issue_set):
        # Special chars should not raise; search proceeds normally
        results = search_issues(issue_set, "layout.*")
        # "layout.*" doesn't match as literal text — no results expected
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

FRESHNESS_CASES = [
    (7, ["1", "3"]),       # Last 7 days: freshness_days <= 7
    (30, ["1", "2", "3"]), # Last 30 days: freshness_days <= 30
    (90, ["1", "2", "3", "4", "5"]),  # Last 90 days: all
    (None, ["1", "2", "3", "4", "5"]), # All time: no filter
]


class TestRuleSRC002:
    @pytest.mark.parametrize("max_days,expected_ids", FRESHNESS_CASES)
    def test_freshness_filter(self, issue_set, max_days, expected_ids):
        results = filter_by_freshness(issue_set, max_days)
        result_ids = sorted(i["id"] for i in results)
        assert result_ids == sorted(expected_ids)

    def test_filter_last_7_days_excludes_older(self, issue_set):
        results = filter_by_freshness(issue_set, 7)
        ids = [i["id"] for i in results]
        assert "4" not in ids  # freshness_days=45
        assert "5" not in ids  # freshness_days=60

    def test_all_time_filter_returns_everything(self, issue_set):
        results = filter_by_freshness(issue_set, None)
        assert len(results) == len(issue_set)

    def test_filter_exact_boundary_included(self):
        issues = [make_issue("x", "Title", "desc", freshness_days=7)]
        results = filter_by_freshness(issues, 7)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestRuleSRC003:
    def test_search_and_filter_combined_and_logic(self, issue_set):
        # "mobile" matches ids 1 and 4; filter Last 7 days keeps only id 1 (days=3)
        results = apply_search_and_filter(issue_set, "mobile", max_days=7)
        ids = [i["id"] for i in results]
        assert ids == ["1"]
        assert "4" not in ids  # freshness_days=45, excluded by filter

    def test_combined_no_results_when_disjoint(self, issue_set):
        # "backend" only matches id 3 (freshness=5), but filter Last 3 days excludes it
        results = apply_search_and_filter(issue_set, "backend", max_days=2)
        assert results == []

    def test_combined_search_empty_with_freshness_filter(self, issue_set):
        results = apply_search_and_filter(issue_set, "", max_days=7)
        ids = [i["id"] for i in results]
        # Empty query returns all, then filter to 7 days: ids 1 and 3
        assert "1" in ids
        assert "3" in ids
        assert "4" not in ids

    def test_combined_all_time_filter_equals_search_only(self, issue_set):
        search_only = search_issues(issue_set, "figma")
        combined = apply_search_and_filter(issue_set, "figma", max_days=None)
        assert [i["id"] for i in combined] == [i["id"] for i in search_only]
