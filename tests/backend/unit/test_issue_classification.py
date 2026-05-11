"""Regression tests for LEVEL8 RULE-CLS-*** (classification)."""

from __future__ import annotations

import pytest

from app.issue_classification import classify_design_issue


def test_design_issue_signals_relevance_for_design_keywords_rule_cls_001() -> None:
    """RULE-CLS-001 scenario: designer-facing issue classified as relevant."""
    outcome = classify_design_issue(
        title="Create wireframes for settings page",
        description="We need mockup, user flow, and collaboration in Figma",
        comments=(),
    )
    assert outcome["classification"] == "relevant"
    assert outcome["is_claimed"] is False


def test_backend_issue_signals_not_relevant_rule_cls_001() -> None:
    """RULE-CLS-001 scenario: engineering-only issue classified as not_relevant."""
    outcome = classify_design_issue(
        title="Fix API endpoint for user auth",
        description="Add database migrations and verify the REST API works",
        comments=(),
    )
    assert outcome["classification"] == "not_relevant"
    assert outcome["is_claimed"] is False


def test_empty_issue_description_always_not_relevant_rule_cls_002() -> None:
    """RULE-CLS-002 empty description shells are excluded."""
    outcome = classify_design_issue(
        title="Spike: landing page tweaks",
        description="",
        comments=(),
    )
    assert outcome["classification"] == "not_relevant"


def test_placeholder_heading_shell_is_not_relevant_rule_cls_002() -> None:
    """RULE-CLS-002 placeholder headings without substantive copy."""
    skeleton = "## Description\n## TODO\n\n## Acceptance Criteria\n"
    outcome = classify_design_issue(title="Improve dashboard", description=skeleton, comments=())
    assert outcome["classification"] == "not_relevant"


@pytest.mark.parametrize(
    ("combined_text",),
    [
        ("We need broader test coverage, add a QA case.",),
        ("Refactor legacy API endpoints before the database migration.",),
        ("Refactor rename X to Y.",),
        ("Please implement in code updates across the entire code base for stability.",),
        ("Export new sprite sheet and bundle UTF files for shipped game assets.",),
    ],
    ids=(
        "qa_testing_verbiage",
        "api_migration_verbiage",
        "pure_refactor_ticket",
        "implementation_only_ticket",
        "game_asset_ticket",
    ),
)
def test_exclusion_categories_force_not_relevant_rule_cls_004(combined_text: str) -> None:
    """RULE-CLS-004 exclusions override stray design-ish wording."""
    outcome = classify_design_issue(
        title="Internal maintenance",
        description=combined_text,
        comments=(),
    )
    assert outcome["classification"] == "not_relevant"


def test_claimed_but_relevant_issue_sets_claim_flag_rule_cls_003() -> None:
    """RULE-CLS-003 design issue stays relevant while surfacing Claim signal."""
    outcome = classify_design_issue(
        title="Refresh contributor onboarding visuals",
        description="We need approachable illustrations for the empty state artwork",
        comments=("I'm taking this on",),
    )
    assert outcome["classification"] == "relevant"
    assert outcome["is_claimed"] is True
