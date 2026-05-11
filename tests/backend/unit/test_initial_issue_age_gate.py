"""Regression tests for LEVEL8 RULE-ETL-002 (initial fetch age exclusions)."""

from __future__ import annotations

from app.initial_fetch_gate import discard_issue_on_age_for_reset


def test_centenarian_issues_drop_from_initial_capture_rule_etl_002() -> None:
    """RULE-ETL-002 scenario: stale GitHub Issues never enter DuckDB."""
    assert discard_issue_on_age_for_reset(days_since_github_creation=100) is True


def test_recent_issue_survives_initial_capture_rule_etl_002() -> None:
    """RULE-ETL-002 scenario: youthful issues remain eligible."""
    assert discard_issue_on_age_for_reset(days_since_github_creation=30) is False
