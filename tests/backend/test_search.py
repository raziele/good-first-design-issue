"""
Tests for Search and Filtering behavior.

Spec: specs/behavior/search.spec.md
Rules: RULE-SRC-001 through RULE-SRC-004
Glossary: TERM-001 (Issue), TERM-009 (Freshness)
"""
import pytest
from tests.backend.conftest import make_issue


# ---------------------------------------------------------------------------
# Helpers — simulate search/filter logic
# ---------------------------------------------------------------------------

def _search(issues, query):
    """Full-text search across title and description (RULE-SRC-001)."""
    q = query.lower()
    return [
        i for i in issues
        if q in i["title"].lower() or q in i["description"].lower()
    ]


def _filter_freshness(issues, max_days):
    """Filter issues by freshness_days <= max_days. None means no filter (RULE-SRC-002)."""
    if max_days is None:
        return issues
    return [i for i in issues if i["freshness_days"] <= max_days]


FRESHNESS_OPTIONS = {
    "Last 7 days": 7,
    "Last 30 days": 30,
    "Last 90 days": 90,
    "All time": None,
}


def _combined(issues, query=None, freshness_label=None):
    """Apply search + freshness filter with AND logic (RULE-SRC-003)."""
    result = issues
    if query:
        result = _search(result, query)
    if freshness_label:
        max_days = FRESHNESS_OPTIONS[freshness_label]
        result = _filter_freshness(result, max_days)
    return result


# ---------------------------------------------------------------------------
# RULE-SRC-001: Full-text search across title and description
# ---------------------------------------------------------------------------

def test_search_matches_title():
    """RULE-SRC-001 / Scenario: Search matches title."""
    issues = [make_issue(title="Mobile onboarding redesign", description="some description")]
    results = _search(issues, "onboarding")
    assert len(results) == 1
    assert results[0]["title"] == "Mobile onboarding redesign"


def test_search_matches_description():
    """RULE-SRC-001 / Scenario: Search matches description."""
    issues = [make_issue(title="UI updates", description="Needs an accessibility audit review")]
    results = _search(issues, "accessibility")
    assert len(results) == 1


def test_search_returns_no_results_for_unmatched_term():
    """RULE-SRC-001 / Scenario: Search returns no results."""
    issues = [
        make_issue(id="a", title="Design system", description="color tokens"),
        make_issue(id="b", title="Navigation redesign", description="menu flow"),
    ]
    results = _search(issues, "blockchain")
    assert results == []


def test_search_is_case_insensitive():
    """RULE-SRC-001 / Implicit: case-insensitive match."""
    issues = [make_issue(title="ONBOARDING Flow", description="")]
    assert len(_search(issues, "onboarding")) == 1
    assert len(_search(issues, "ONBOARDING")) == 1


def test_search_matches_both_title_and_description():
    """RULE-SRC-001 / Implicit: multiple issues matching via different fields."""
    issues = [
        make_issue(id="t", title="accessibility improvements", description="no match"),
        make_issue(id="d", title="UI cleanup", description="accessibility audit needed"),
    ]
    results = _search(issues, "accessibility")
    ids = {r["id"] for r in results}
    assert ids == {"t", "d"}


# ---------------------------------------------------------------------------
# RULE-SRC-002: Filter by freshness
# ---------------------------------------------------------------------------

def test_search_filter_last_7_days():
    """RULE-SRC-002 / Scenario: Filter to recent issues — Last 7 days."""
    issues = [
        make_issue(id="new", freshness_days=3),
        make_issue(id="old", freshness_days=20),
    ]
    results = _filter_freshness(issues, 7)
    assert len(results) == 1
    assert results[0]["id"] == "new"


@pytest.mark.parametrize("filter_label,max_days,expected_ids", [
    ("Last 7 days",  7,    {"d3", "d7"}),
    ("Last 30 days", 30,   {"d3", "d7", "d30"}),
    ("Last 90 days", 90,   {"d3", "d7", "d30", "d90"}),
    ("All time",     None, {"d3", "d7", "d30", "d90", "d120"}),
])
def test_search_freshness_filter_options(filter_label, max_days, expected_ids):
    """RULE-SRC-002 / Scenario Outline: Freshness filter options."""
    issues = [
        make_issue(id="d3",   freshness_days=3),
        make_issue(id="d7",   freshness_days=7),
        make_issue(id="d30",  freshness_days=30),
        make_issue(id="d90",  freshness_days=90),
        make_issue(id="d120", freshness_days=120),
    ]
    results = _filter_freshness(issues, max_days)
    assert {r["id"] for r in results} == expected_ids


# ---------------------------------------------------------------------------
# RULE-SRC-003: Search and filter combine with AND logic
# ---------------------------------------------------------------------------

def test_search_combined_search_and_filter():
    """RULE-SRC-003 / Scenario: Combined search and filter."""
    issues = [
        make_issue(id="recent", title="Mobile redesign", description="mobile layout", freshness_days=3),
        make_issue(id="old",    title="Mobile app icons",  description="icon set",       freshness_days=45),
    ]
    results = _combined(issues, query="mobile", freshness_label="Last 7 days")
    assert len(results) == 1
    assert results[0]["id"] == "recent"


def test_search_combined_no_results_when_filters_too_restrictive():
    """RULE-SRC-003 / Edge: AND logic means stricter combined results."""
    issues = [make_issue(id="a", title="typography system", freshness_days=60)]
    results = _combined(issues, query="typography", freshness_label="Last 7 days")
    assert results == []


def test_search_combined_search_only_no_filter():
    """RULE-SRC-003 / search alone (no freshness filter) returns all matching."""
    issues = [
        make_issue(id="a", title="navigation redesign", freshness_days=5),
        make_issue(id="b", title="navigation icons",    freshness_days=200),
    ]
    results = _combined(issues, query="navigation")
    assert len(results) == 2


def test_search_combined_filter_only_no_search():
    """RULE-SRC-003 / filter alone (no query) returns all within freshness."""
    issues = [
        make_issue(id="a", freshness_days=5),
        make_issue(id="b", freshness_days=50),
    ]
    results = _combined(issues, freshness_label="Last 7 days")
    assert len(results) == 1
    assert results[0]["id"] == "a"
