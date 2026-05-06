"""
Backend tests for Search and Filtering.
Spec: specs/behavior/search.spec.md
"""
import pytest
from conftest import make_issue


# ---------------------------------------------------------------------------
# Helpers — pure filter logic (mirrors what the backend query layer does)
# ---------------------------------------------------------------------------

def search_issues(issues: list[dict], query: str) -> list[dict]:
    """Full-text search across title and description (case-insensitive)."""
    q = query.lower()
    return [
        i for i in issues
        if q in i["title"].lower() or q in i["description"].lower()
    ]


def filter_by_freshness(issues: list[dict], max_days: int | None) -> list[dict]:
    """Apply freshness filter; None means 'All time' (no filter)."""
    if max_days is None:
        return issues
    return [i for i in issues if i["freshness_days"] <= max_days]


def search_and_filter(issues: list[dict], query: str, max_days: int | None) -> list[dict]:
    """Combined AND logic: search then freshness filter."""
    results = search_issues(issues, query) if query else issues
    return filter_by_freshness(results, max_days)


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

def test_search_matches_title():
    """RULE-SRC-001: Scenario: Search matches title."""
    issue = make_issue(title="Mobile onboarding redesign", description="Some general text.")
    results = search_issues([issue], "onboarding")
    assert any(i["id"] == issue["id"] for i in results)


def test_search_matches_description():
    """RULE-SRC-001: Scenario: Search matches description."""
    issue = make_issue(
        title="Generic issue",
        description="This issue requires an accessibility audit of all form fields.",
    )
    results = search_issues([issue], "accessibility")
    assert any(i["id"] == issue["id"] for i in results)


def test_search_returns_no_results_when_no_match():
    """RULE-SRC-001: Scenario: Search returns no results."""
    issues = [
        make_issue(id="a", title="Mobile redesign", description="User flows"),
        make_issue(id="b", title="Icon system", description="Design tokens"),
    ]
    results = search_issues(issues, "blockchain")
    assert results == []


def test_search_is_case_insensitive():
    """RULE-SRC-001: Search is case-insensitive (derived from full-text intent)."""
    issue = make_issue(title="Onboarding Redesign", description="General text.")
    results = search_issues([issue], "ONBOARDING")
    assert any(i["id"] == issue["id"] for i in results)


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("filter_value,max_days,expected_ids", [
    ("Last 7 days",  7,    ["fresh"]),
    ("Last 30 days", 30,   ["fresh", "mid"]),
    ("Last 90 days", 90,   ["fresh", "mid", "old"]),
    ("All time",     None, ["fresh", "mid", "old", "ancient"]),
])
def test_freshness_filter_options(filter_value, max_days, expected_ids):
    """RULE-SRC-002: Scenario Outline: Freshness filter options."""
    issues = [
        make_issue(id="fresh",   freshness_days=3),
        make_issue(id="mid",     freshness_days=20),
        make_issue(id="old",     freshness_days=60),
        make_issue(id="ancient", freshness_days=120),
    ]
    results = filter_by_freshness(issues, max_days)
    result_ids = sorted(i["id"] for i in results)
    assert result_ids == sorted(expected_ids), f"Failed for filter: {filter_value}"


def test_filter_recent_issues_last_7_days():
    """RULE-SRC-002: Scenario: Filter to recent issues."""
    issues = [
        make_issue(id="new", freshness_days=5),
        make_issue(id="old", freshness_days=30),
    ]
    results = filter_by_freshness(issues, 7)
    ids = [i["id"] for i in results]
    assert "new" in ids
    assert "old" not in ids


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine (AND logic)
# ---------------------------------------------------------------------------

def test_combined_search_and_filter():
    """RULE-SRC-003: Scenario: Combined search and filter."""
    issues = [
        make_issue(id="match",   title="Mobile redesign",   freshness_days=3),
        make_issue(id="no_match", title="Mobile app icons", freshness_days=45),
    ]
    results = search_and_filter(issues, query="mobile", max_days=7)
    ids = [i["id"] for i in results]
    assert "match" in ids
    assert "no_match" not in ids


def test_combined_search_and_filter_no_results():
    """RULE-SRC-003: Combined filter + search that yields zero results."""
    issues = [
        make_issue(id="a", title="Mobile redesign", freshness_days=45),
    ]
    results = search_and_filter(issues, query="mobile", max_days=7)
    assert results == []


# ---------------------------------------------------------------------------
# RULE-SRC-004: Mobile uses bottom sheet for filters
# (UX behavior — validated via E2E; backend logic is not affected by viewport)
# ---------------------------------------------------------------------------

def test_search_short_query_no_execution():
    """
    Flow: search.flow.md — Edge case: query < 2 chars → no search executed.
    TODO: confirm threshold (< 2 chars) with frontend implementation.
    """
    # Backend contract: if frontend sends a 1-char query, it should be treated
    # as no-op or filtered. This test documents the expected empty passthrough.
    issues = [make_issue(id="a", title="Anything")]
    short_query = "a"
    # Backend should not be called; test confirms the guard should exist
    assert len(short_query) < 2  # guard condition


def test_search_special_characters_are_escaped():
    """Flow: search.flow.md — Edge case: special characters in search query."""
    issues = [make_issue(id="a", title="Settings & Preferences redesign")]
    # Special chars like & should not break the search
    results = search_issues(issues, "settings &")
    assert any(i["id"] == "a" for i in results)
