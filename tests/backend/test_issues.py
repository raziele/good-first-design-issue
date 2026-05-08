"""Tests for RULE-ISS-001 through RULE-ISS-005: Issue Browsing and Viewing."""
import pytest
from app.issues import filter_issues, sort_issues_by_freshness, truncate_description


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

def test_filter_issues_includes_relevant_active(relevant_active_issue):
    """RULE-ISS-001 — relevant + active issue appears in listing."""
    result = filter_issues([relevant_active_issue])
    assert len(result) == 1
    assert result[0]["id"] == relevant_active_issue["id"]


def test_filter_issues_excludes_not_relevant(not_relevant_issue):
    """RULE-ISS-001 — not_relevant issue is excluded from listing."""
    result = filter_issues([not_relevant_issue])
    assert len(result) == 0


def test_filter_issues_excludes_archived(archived_issue):
    """RULE-ISS-001 — archived issue is excluded from listing."""
    result = filter_issues([archived_issue])
    assert len(result) == 0


def test_filter_issues_combined(relevant_active_issue, not_relevant_issue, archived_issue):
    """RULE-ISS-001 — only relevant+active issues survive mixed input."""
    result = filter_issues([relevant_active_issue, not_relevant_issue, archived_issue])
    assert len(result) == 1
    assert result[0]["id"] == relevant_active_issue["id"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card truncated description ~200 chars
# ---------------------------------------------------------------------------

def test_truncate_description_short_stays_unchanged():
    """RULE-ISS-002 — descriptions under 200 chars are not truncated."""
    short = "Short description."
    assert truncate_description(short) == short


def test_truncate_description_long_is_cut_at_200_chars():
    """RULE-ISS-002 — descriptions over 200 chars are truncated to ~200 chars."""
    long_desc = "A" * 300
    result = truncate_description(long_desc)
    assert len(result) <= 203  # 200 chars + possible ellipsis ("...")


def test_truncate_description_long_ends_with_ellipsis():
    """RULE-ISS-002 — truncated descriptions end with ellipsis."""
    long_desc = "Word " * 100
    result = truncate_description(long_desc)
    assert result.endswith("...")


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

def test_filter_issues_includes_claimed_relevant(claimed_relevant_issue):
    """RULE-ISS-004 — claimed but relevant+active issue still appears in listing."""
    result = filter_issues([claimed_relevant_issue])
    assert len(result) == 1
    assert result[0]["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness (ascending freshness_days)
# ---------------------------------------------------------------------------

def test_sort_issues_by_freshness_newest_first():
    """RULE-ISS-005 — issues sorted by freshness_days ascending (newest first)."""
    issues = [
        {"id": "a", "freshness_days": 30, "classification": "relevant", "status": "active"},
        {"id": "b", "freshness_days": 2, "classification": "relevant", "status": "active"},
        {"id": "c", "freshness_days": 15, "classification": "relevant", "status": "active"},
    ]
    sorted_issues = sort_issues_by_freshness(issues)
    assert [i["id"] for i in sorted_issues] == ["b", "c", "a"]
