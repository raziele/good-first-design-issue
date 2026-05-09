"""
Tests for Search and Filtering rules.
RULE-SRC-001: Full-text search across title and description
RULE-SRC-002: Filter by freshness
RULE-SRC-003: Search and filter combine (AND logic)
RULE-SRC-004: Mobile uses bottom sheet for filters (behavior contract: filter logic unchanged)
"""

import pytest
from app.search import search_issues, apply_freshness_filter, combine_search_and_filter


def _make_issue(id, title, description, freshness_days):
    return {
        "id": id,
        "title": title,
        "description": description,
        "freshness_days": freshness_days,
        "classification": "relevant",
        "status": "active",
    }


ISSUE_FIXTURES = [
    _make_issue("iss-1", "Mobile onboarding redesign", "Full ux audit needed", 3),
    _make_issue("iss-2", "Settings page layout", "accessibility audit required", 20),
    _make_issue("iss-3", "Mobile app icons", "Icon set redesign", 45),
    _make_issue("iss-4", "Backend refactor", "database migration task", 5),
]


class TestRuleSRC001FullTextSearch:
    """RULE-SRC-001: Full-text search across title and description."""

    def test_search_matches_title(self):
        """Search query matching a title returns the corresponding issue."""
        results = search_issues(ISSUE_FIXTURES, query="onboarding")
        ids = [r["id"] for r in results]
        assert "iss-1" in ids

    def test_search_matches_description(self):
        """Search query matching description text returns the corresponding issue."""
        results = search_issues(ISSUE_FIXTURES, query="accessibility")
        ids = [r["id"] for r in results]
        assert "iss-2" in ids

    def test_search_no_results_for_unknown_term(self):
        """Search with a term present in no issues returns empty list."""
        results = search_issues(ISSUE_FIXTURES, query="blockchain")
        assert results == []

    def test_search_is_case_insensitive(self):
        """Search is case-insensitive (spec: full-text across title and description)."""
        results = search_issues(ISSUE_FIXTURES, query="ONBOARDING")
        ids = [r["id"] for r in results]
        assert "iss-1" in ids


class TestRuleSRC002FreshnessFilter:
    """RULE-SRC-002: Filter by freshness — only filter dimension in v1."""

    @pytest.mark.parametrize(
        "filter_days,expected_ids",
        [
            (7, ["iss-1", "iss-4"]),       # Last 7 days: freshness_days <= 7
            (30, ["iss-1", "iss-2", "iss-4"]),  # Last 30 days: freshness_days <= 30
            (90, ["iss-1", "iss-2", "iss-3", "iss-4"]),  # Last 90 days: all
            (None, ["iss-1", "iss-2", "iss-3", "iss-4"]),  # All time: no filter
        ],
    )
    def test_freshness_filter(self, filter_days, expected_ids):
        """Freshness filter includes only issues with freshness_days <= filter_days."""
        results = apply_freshness_filter(ISSUE_FIXTURES, max_days=filter_days)
        result_ids = sorted(r["id"] for r in results)
        assert result_ids == sorted(expected_ids)


class TestRuleSRC003CombinedSearchAndFilter:
    """RULE-SRC-003: Search and filter combine with AND logic."""

    def test_combined_search_and_freshness_filter(self):
        """Only issues matching BOTH search term AND freshness filter appear."""
        # "Mobile redesign" (iss-1, 3 days) should match; "Mobile app icons" (iss-3, 45 days) should not.
        results = combine_search_and_filter(
            ISSUE_FIXTURES,
            query="mobile",
            max_freshness_days=7,
        )
        ids = [r["id"] for r in results]
        assert "iss-1" in ids
        assert "iss-3" not in ids

    def test_no_results_when_filter_excludes_all_matches(self):
        """Returns empty when search matches but freshness filter excludes all matches."""
        results = combine_search_and_filter(
            ISSUE_FIXTURES,
            query="icons",  # only iss-3 at 45 days
            max_freshness_days=7,
        )
        assert results == []
