"""Regression tests for LEVEL8 RULE-ETL-004 closed GitHub Issues → Archive."""

from __future__ import annotations

from app.github_issue_lifecycle import browse_status_when_github_reports_closed


def test_closed_github_issue_archives_issue_record_rule_etl_004() -> None:
    snapshot = browse_status_when_github_reports_closed(github_issue_closed=True, prior_status="active")
    assert snapshot["status"] == "archived"
