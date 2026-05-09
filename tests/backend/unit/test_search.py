"""
Tests for RULE-SRC-001 through RULE-SRC-003: Search and filtering behavior.
SUT: app.search
"""
import pytest
from app.search import search_issues, apply_freshness_filter, combine_search_and_filter


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

class TestFullTextSearch:
    def test_search_matches_title(self):
        """RULE-SRC-001: Search query matching a word in the issue title returns the issue."""
        issues = [
            {"id": "1", "title": "Mobile onboarding redesign", "description": ""},
        ]
        result = search_issues(issues, query="onboarding")
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_search_matches_description(self):
        """RULE-SRC-001: Search query matching a word in the description returns the issue."""
        issues = [
            {"id": "2", "title": "Some issue", "description": "We need an accessibility audit."},
        ]
        result = search_issues(issues, query="accessibility")
        assert len(result) == 1
        assert result[0]["id"] == "2"

    def test_search_returns_no_results_when_no_match(self):
        """RULE-SRC-001: Search for a term not in any issue returns empty list."""
        issues = [
            {"id": "1", "title": "Mobile redesign", "description": "UI improvements"},
        ]
        result = search_issues(issues, query="blockchain")
        assert result == []

    def test_search_is_case_insensitive(self):
        """RULE-SRC-001: Search is case-insensitive."""
        issues = [
            {"id": "1", "title": "Onboarding Flow", "description": ""},
        ]
        result = search_issues(issues, query="onboarding")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filter_value,max_days,ids_expected", [
    ("Last 7 days", 7, ["recent"]),
    ("Last 30 days", 30, ["recent", "mid"]),
    ("Last 90 days", 90, ["recent", "mid", "older"]),
    ("All time", None, ["recent", "mid", "older", "ancient"]),
])
def test_freshness_filter_options(filter_value, max_days, ids_expected):
    """RULE-SRC-002: Freshness filter correctly limits results per filter option."""
    issues = [
        {"id": "recent", "freshness_days": 3},
        {"id": "mid", "freshness_days": 20},
        {"id": "older", "freshness_days": 60},
        {"id": "ancient", "freshness_days": 180},
    ]
    result = apply_freshness_filter(issues, max_days=max_days)
    assert sorted(i["id"] for i in result) == sorted(ids_expected)


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

class TestSearchAndFilterCombined:
    def test_combined_search_and_freshness_filter(self):
        """RULE-SRC-003: Search + freshness filter combines as AND logic."""
        issues = [
            {"id": "a", "title": "Mobile redesign", "description": "", "freshness_days": 3},
            {"id": "b", "title": "Mobile app icons", "description": "", "freshness_days": 45},
        ]
        result = combine_search_and_filter(issues, query="mobile", max_days=7)
        assert len(result) == 1
        assert result[0]["id"] == "a"

    def test_combined_no_results_when_search_mismatches(self):
        """RULE-SRC-003: No results when search term absent despite freshness match."""
        issues = [
            {"id": "a", "title": "Illustration work", "description": "", "freshness_days": 2},
        ]
        result = combine_search_and_filter(issues, query="mobile", max_days=7)
        assert result == []

    def test_combined_no_results_when_too_old(self):
        """RULE-SRC-003: No results when issue matches search but falls outside freshness window."""
        issues = [
            {"id": "a", "title": "Mobile app icons", "description": "", "freshness_days": 45},
        ]
        result = combine_search_and_filter(issues, query="mobile", max_days=7)
        assert result == []
