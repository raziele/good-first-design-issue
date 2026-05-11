"""Regression tests for LEVEL8 RULE-ISS-*** (listing visibility facets)."""

from __future__ import annotations

from app.issue_homepage_policy import (
    homepage_issue_claim_badge_label,
    homepage_issue_visibility,
)


def test_relevant_active_issue_surfaces_rule_iss_001() -> None:
    """RULE-ISS-001 scenario: eligible Relevant Issues appear."""
    snapshot = {"classification": "relevant", "status": "active", "freshness_days": 4}
    assert homepage_issue_visibility(snapshot) == "eligible"


def test_not_relevant_issue_hidden_rule_iss_001() -> None:
    """RULE-ISS-001 scenario: Not Relevant Issues stay off home listing."""
    snapshot = {"classification": "not_relevant", "status": "active", "freshness_days": 9}
    assert homepage_issue_visibility(snapshot) == "hidden"


def test_archived_issue_hidden_rule_iss_001() -> None:
    """RULE-ISS-001 scenario: archived content leaves primary listing."""
    snapshot = {"classification": "relevant", "status": "archived", "freshness_days": 55}
    assert homepage_issue_visibility(snapshot) == "hidden"


def test_claimed_issues_surface_helper_copy_rule_iss_004() -> None:
    """RULE-ISS-004 surfaced Claim metadata without blocking downstream CTAs."""
    snapshot = {"classification": "relevant", "status": "active", "is_claimed": True, "freshness_days": 12}
    assert homepage_issue_claim_badge_label(snapshot) == "Already claimed"


def test_unclaimed_issues_omit_claim_badge_copy_rule_iss_004() -> None:
    snapshot = {"classification": "relevant", "status": "active", "is_claimed": False, "freshness_days": 4}
    assert homepage_issue_claim_badge_label(snapshot) == ""
