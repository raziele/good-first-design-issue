"""Tests for RULE-SRC-001 through RULE-SRC-003: Search and Filtering."""
import pytest
from app.search import search_issues, apply_freshness_filter, combine_search_and_filter


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

def test_search_matches_title():
    """RULE-SRC-001 — search term matching issue title returns the issue."""
    issues = [
        {"id": "a", "title": "Mobile onboarding redesign", "description": "Improve the flow."},
    ]
    result = search_issues(issues, "onboarding")
    assert len(result) == 1
    assert result[0]["id"] == "a"


def test_search_matches_description():
    """RULE-SRC-001 — search term matching issue description returns the issue."""
    issues = [
        {"id": "b", "title": "Improve accessibility", "description": "Run an accessibility audit."},
    ]
    result = search_issues(issues, "accessibility")
    assert len(result) == 1
    assert result[0]["id"] == "b"


def test_search_returns_empty_when_no_match():
    """RULE-SRC-001 — search with no matches returns empty list."""
    issues = [
        {"id": "c", "title": "Mobile redesign", "description": "UX improvements."},
    ]
    result = search_issues(issues, "blockchain")
    assert result == []


def test_search_is_case_insensitive():
    """RULE-SRC-001 — search is case-insensitive."""
    issues = [
        {"id": "d", "title": "Mobile Onboarding Redesign", "description": ""},
    ]
    result = search_issues(issues, "onboarding")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filter_value,max_days,expected_ids", [
    ("Last 7 days", 7, ["new"]),
    ("Last 30 days", 30, ["new", "recent"]),
    ("Last 90 days", 90, ["new", "recent", "older"]),
    ("All time", None, ["new", "recent", "older", "ancient"]),
])
def test_freshness_filter_options(filter_value, max_days, expected_ids):
    """RULE-SRC-002 — freshness filter returns issues within the specified window."""
    issues = [
        {"id": "new", "freshness_days": 3},
        {"id": "recent", "freshness_days": 20},
        {"id": "older", "freshness_days": 60},
        {"id": "ancient", "freshness_days": 120},
    ]
    result = apply_freshness_filter(issues, max_days)
    result_ids = [i["id"] for i in result]
    for eid in expected_ids:
        assert eid in result_ids, f"Expected '{eid}' in results for filter '{filter_value}'"
    assert len(result) == len(expected_ids)


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

def test_search_and_filter_combine_and_logic():
    """RULE-SRC-003 — combined search + freshness filter uses AND logic."""
    issues = [
        {"id": "match_both", "title": "Mobile redesign", "description": "", "freshness_days": 3},
        {"id": "title_match_stale", "title": "Mobile app icons", "description": "", "freshness_days": 45},
        {"id": "fresh_no_title", "title": "Backend refactor", "description": "", "freshness_days": 2},
    ]
    result = combine_search_and_filter(issues, query="mobile", max_freshness_days=7)
    assert len(result) == 1
    assert result[0]["id"] == "match_both"
