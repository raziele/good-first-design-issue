"""Regression tests for LEVEL8 RULE-ISS-005 (default browse ordering)."""

from __future__ import annotations

from app.issue_sorting import order_issues_for_homepage


def test_default_homepage_sort_prioritizes_fresh_issues_rule_iss_005() -> None:
    """RULE-ISS-005 freshness sort uses ascending freshness_days (most recent first)."""
    unordered = (
        {"id": "9", "freshness_days": 30},
        {"id": "2", "freshness_days": 3},
        {"id": "4", "freshness_days": 10},
    )
    ordered_ids = tuple(item["id"] for item in order_issues_for_homepage(unordered))
    assert ordered_ids == ("2", "4", "9")
