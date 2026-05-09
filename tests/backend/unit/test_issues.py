"""
Tests for Issue Browsing and Viewing rules.
RULE-ISS-001: Display only relevant active issues
RULE-ISS-002: Issue card displays preview information
RULE-ISS-003: Issue detail view shows full information
RULE-ISS-004: Claimed issues are marked
RULE-ISS-005: Default sort is by freshness
"""

import pytest
from app.issues import filter_listable_issues, sort_by_freshness, truncate_description


# ---------------------------------------------------------------------------
# Shared fixtures live in conftest.py; minimal inline data for clarity.
# ---------------------------------------------------------------------------

def _make_issue(**overrides):
    base = {
        "id": "iss-1",
        "title": "Redesign settings page",
        "description": "Full description text here.",
        "repo_name": "owner/repo",
        "repo_stars": 42,
        "classification": "relevant",
        "status": "active",
        "is_claimed": False,
        "freshness_days": 5,
        "complexity_score": "medium",
        "attractiveness_rating": 0.8,
        "seniority_level": "junior",
        "has_media": False,
        "github_url": "https://github.com/owner/repo/issues/1",
    }
    base.update(overrides)
    return base


class TestRuleISS001DisplayOnlyRelevantActive:
    """RULE-ISS-001: Only relevant+active issues appear in the main listing."""

    def test_relevant_active_issue_appears(self):
        """Relevant and active issue is included in listing."""
        issues = [_make_issue(classification="relevant", status="active")]
        result = filter_listable_issues(issues)
        assert len(result) == 1

    def test_not_relevant_issue_is_excluded(self):
        """Not-relevant issue is excluded from listing."""
        issues = [_make_issue(classification="not_relevant", status="active")]
        result = filter_listable_issues(issues)
        assert len(result) == 0

    def test_archived_issue_is_excluded(self):
        """Archived issue is excluded from main listing."""
        issues = [_make_issue(classification="relevant", status="archived")]
        result = filter_listable_issues(issues)
        assert len(result) == 0

    def test_not_relevant_and_archived_both_excluded(self):
        """Both not_relevant and archived issues are excluded together."""
        issues = [
            _make_issue(id="a", classification="not_relevant", status="active"),
            _make_issue(id="b", classification="relevant", status="archived"),
            _make_issue(id="c", classification="relevant", status="active"),
        ]
        result = filter_listable_issues(issues)
        assert len(result) == 1
        assert result[0]["id"] == "c"


class TestRuleISS002CardTruncation:
    """RULE-ISS-002: Issue card description is truncated to ~200 chars."""

    def test_long_description_truncated_to_200_chars(self):
        """Description longer than 200 chars is truncated."""
        long_desc = "A" * 500
        truncated = truncate_description(long_desc, max_chars=200)
        assert len(truncated) <= 200

    def test_short_description_not_truncated(self):
        """Description shorter than 200 chars is returned intact."""
        short_desc = "Short description."
        truncated = truncate_description(short_desc, max_chars=200)
        assert truncated == short_desc

    def test_truncated_description_ends_with_ellipsis(self):
        """Truncated description ends with an ellipsis marker."""
        long_desc = "B" * 500
        truncated = truncate_description(long_desc, max_chars=200)
        assert truncated.endswith("…") or truncated.endswith("...")


class TestRuleISS004ClaimedIssues:
    """RULE-ISS-004: Claimed issues appear but are marked."""

    def test_claimed_issue_is_included_in_listing(self):
        """Claimed issues (is_claimed=True) are NOT hidden — they still appear."""
        issues = [_make_issue(is_claimed=True, classification="relevant", status="active")]
        result = filter_listable_issues(issues)
        assert len(result) == 1

    def test_claimed_flag_preserved_through_filter(self):
        """is_claimed attribute is preserved on filtered issues."""
        issues = [_make_issue(is_claimed=True, classification="relevant", status="active")]
        result = filter_listable_issues(issues)
        assert result[0]["is_claimed"] is True


class TestRuleISS005DefaultSortByFreshness:
    """RULE-ISS-005: Default sort is by freshness (ascending freshness_days = newest first)."""

    def test_issues_sorted_by_freshness_ascending(self):
        """Issues are ordered by freshness_days ascending (lowest value = most recent)."""
        issues = [
            _make_issue(id="old", freshness_days=30),
            _make_issue(id="new", freshness_days=2),
            _make_issue(id="mid", freshness_days=10),
        ]
        sorted_issues = sort_by_freshness(issues)
        ids = [i["id"] for i in sorted_issues]
        assert ids == ["new", "mid", "old"]
