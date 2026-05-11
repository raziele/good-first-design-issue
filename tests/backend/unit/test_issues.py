"""Tests for issue browsing rules: RULE-ISS-001, RULE-ISS-002, RULE-ISS-004, RULE-ISS-005."""

from __future__ import annotations

import pytest

from app.issues import filter_listable_issues, sort_issues_by_freshness, truncate_description


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------


def _issue(
    *,
    id: str = "1",
    classification: str = "relevant",
    status: str = "active",
    is_claimed: bool = False,
    freshness_days: int = 5,
    title: str = "Test issue",
    description: str = "A description",
    repo_name: str = "org/repo",
    repo_stars: int = 100,
    complexity_score: str = "low",
    attractiveness_rating: float = 0.8,
    seniority_level: str = "junior",
    has_media: bool = False,
) -> dict:
    return {
        "id": id,
        "classification": classification,
        "status": status,
        "is_claimed": is_claimed,
        "freshness_days": freshness_days,
        "title": title,
        "description": description,
        "repo_name": repo_name,
        "repo_stars": repo_stars,
        "complexity_score": complexity_score,
        "attractiveness_rating": attractiveness_rating,
        "seniority_level": seniority_level,
        "has_media": has_media,
    }


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------


def test_relevant_active_issue_appears_in_listing():
    """RULE-ISS-001 / Scenario: Relevant active issue appears in listing."""
    issues = [_issue(classification="relevant", status="active")]
    result = filter_listable_issues(issues)
    assert len(result) == 1


def test_not_relevant_issue_is_hidden():
    """RULE-ISS-001 / Scenario: Not-relevant issue is hidden."""
    issues = [_issue(classification="not_relevant", status="active")]
    result = filter_listable_issues(issues)
    assert result == []


def test_archived_issue_is_hidden_from_main_listing():
    """RULE-ISS-001 / Scenario: Archived issue is hidden from main listing."""
    issues = [_issue(classification="relevant", status="archived")]
    result = filter_listable_issues(issues)
    assert result == []


def test_closed_issue_is_hidden_from_main_listing():
    """RULE-ISS-001 / Closed issues must not appear in main listing."""
    issues = [_issue(classification="relevant", status="closed")]
    result = filter_listable_issues(issues)
    assert result == []


def test_mixed_issues_returns_only_relevant_active():
    """RULE-ISS-001 / Only the qualifying subset is returned."""
    issues = [
        _issue(id="1", classification="relevant", status="active"),
        _issue(id="2", classification="not_relevant", status="active"),
        _issue(id="3", classification="relevant", status="archived"),
    ]
    result = filter_listable_issues(issues)
    assert [i["id"] for i in result] == ["1"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Truncated description — ~200 chars
# ---------------------------------------------------------------------------


def test_short_description_is_not_truncated():
    """RULE-ISS-002 / Short descriptions pass through unchanged."""
    desc = "Short text."
    assert truncate_description(desc) == desc


def test_long_description_truncated_to_200_chars():
    """RULE-ISS-002 / Descriptions longer than 200 chars are truncated."""
    desc = "A" * 300
    result = truncate_description(desc)
    assert len(result) <= 200


def test_truncated_description_ends_with_ellipsis():
    """RULE-ISS-002 / Truncated descriptions get an ellipsis."""
    desc = "B" * 300
    result = truncate_description(desc)
    assert result.endswith("...")


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness (ascending freshness_days = newest first)
# ---------------------------------------------------------------------------


def test_issues_sorted_by_freshness_ascending():
    """RULE-ISS-005 / Scenario: Listing default sort order — newest first."""
    issues = [
        _issue(id="old", freshness_days=30),
        _issue(id="new", freshness_days=2),
        _issue(id="mid", freshness_days=10),
    ]
    result = sort_issues_by_freshness(issues)
    assert [i["id"] for i in result] == ["new", "mid", "old"]
