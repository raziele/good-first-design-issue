"""Regression tests for LEVEL8 RULE-CLM-*** (claim ergonomics policy)."""

from __future__ import annotations

import pytest

from app.claim_flow_guardrails import claim_sheet_remains_open_for_extra_volunteers

from app.issue_claim_voice import render_contextual_claim_comment_stub


def test_second_volunteers_keep_open_paths_rule_clm_004() -> None:
    """RULE-CLM-004 multiple designers retain identical affordances."""
    assert claim_sheet_remains_open_for_extra_volunteers(prior_logged=True) is True


def test_claim_comment_reflects_issue_context_voice_rule_clm_002() -> None:
    """RULE-CLM-002 deterministic stub echoes Issue anchor tokens until AI wiring arrives."""
    snippet = render_contextual_claim_comment_stub(issue_anchor="mobile onboarding redesign")
    assert "design" in snippet.casefold()
    assert "onboarding" in snippet.casefold()


def test_no_local_claim_persistence_writes_rule_clm_003() -> None:
    """TODO: backend persistence stance documented but durable contract undefined."""
    pytest.skip("RULE-CLM-003 awaits outbound claim telemetry schema before asserting zero rows")
