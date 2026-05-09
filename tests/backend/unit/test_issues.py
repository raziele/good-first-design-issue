"""
Tests for RULE-ISS-001 through RULE-ISS-005: Issue browsing and viewing behavior.
SUT: app.issues
"""
import pytest
from app.issues import filter_relevant_active_issues, sort_by_freshness, truncate_description


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestIssueFiltering:
    def test_relevant_active_issue_appears_in_listing(self):
        """RULE-ISS-001: Issue with classification=relevant and status=active is included."""
        issues = [
            {"id": "1", "classification": "relevant", "status": "active", "title": "Design task"},
        ]
        result = filter_relevant_active_issues(issues)
        assert len(result) == 1
        assert result[0]["id"] == "1"

    def test_not_relevant_issue_is_hidden(self):
        """RULE-ISS-001: Issue with classification=not_relevant is excluded from listing."""
        issues = [
            {"id": "2", "classification": "not_relevant", "status": "active", "title": "Backend task"},
        ]
        result = filter_relevant_active_issues(issues)
        assert len(result) == 0

    def test_archived_issue_is_hidden_from_main_listing(self):
        """RULE-ISS-001: Issue with status=archived is excluded from listing."""
        issues = [
            {"id": "3", "classification": "relevant", "status": "archived", "title": "Old task"},
        ]
        result = filter_relevant_active_issues(issues)
        assert len(result) == 0

    def test_mix_of_issues_filters_correctly(self):
        """RULE-ISS-001: Only relevant+active issues survive filtering from a mixed set."""
        issues = [
            {"id": "1", "classification": "relevant", "status": "active", "title": "Good"},
            {"id": "2", "classification": "not_relevant", "status": "active", "title": "Bad"},
            {"id": "3", "classification": "relevant", "status": "archived", "title": "Old"},
        ]
        result = filter_relevant_active_issues(issues)
        assert [i["id"] for i in result] == ["1"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information (description truncation)
# ---------------------------------------------------------------------------

class TestDescriptionTruncation:
    def test_description_truncated_to_200_chars(self):
        """RULE-ISS-002: Description longer than 200 characters is truncated."""
        long_desc = "A" * 250
        truncated = truncate_description(long_desc, max_chars=200)
        assert len(truncated) <= 203  # 200 chars + possible ellipsis "..."
        assert truncated.endswith("...")

    def test_short_description_not_truncated(self):
        """RULE-ISS-002: Description at or under 200 characters is not truncated."""
        short_desc = "Short description."
        result = truncate_description(short_desc, max_chars=200)
        assert result == short_desc
        assert not result.endswith("...")

    def test_exactly_200_chars_not_truncated(self):
        """RULE-ISS-002: Description of exactly 200 characters is not truncated."""
        exact_desc = "B" * 200
        result = truncate_description(exact_desc, max_chars=200)
        assert result == exact_desc


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness (most recent first)
# ---------------------------------------------------------------------------

class TestIssueSorting:
    def test_issues_sorted_by_freshness_ascending(self):
        """RULE-ISS-005: Issues are sorted by freshness_days ascending (newest first)."""
        issues = [
            {"id": "a", "freshness_days": 30},
            {"id": "b", "freshness_days": 5},
            {"id": "c", "freshness_days": 15},
        ]
        result = sort_by_freshness(issues)
        assert [i["id"] for i in result] == ["b", "c", "a"]

    def test_issues_with_same_freshness_are_stable(self):
        """RULE-ISS-005: Issues with equal freshness preserve relative order."""
        issues = [
            {"id": "x", "freshness_days": 7},
            {"id": "y", "freshness_days": 7},
        ]
        result = sort_by_freshness(issues)
        assert [i["id"] for i in result] == ["x", "y"]
