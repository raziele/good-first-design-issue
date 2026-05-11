"""Regression tests for LEVEL8 RULE-SRC-*** (search & freshness filters)."""

from __future__ import annotations

from app.issue_discovery_filters import narrow_issues_for_discovery

from app.issue_freshness_policy import freshness_upper_bound_days

from app.issue_search_text import issue_matches_terms_in_title_or_body


def test_search_matches_title_case_insensitive_rule_src_001() -> None:
    """RULE-SRC-001: terms hit against issue title."""
    assert issue_matches_terms_in_title_or_body(
        title="Mobile onboarding redesign",
        body="Discuss flows",
        normalized_query_lower="onboarding",
    )


def test_search_matches_description_fragments_rule_src_001() -> None:
    """RULE-SRC-001: queries match descriptive copy."""
    assert issue_matches_terms_in_title_or_body(
        title="Audit checklist",
        body="Conduct a accessibility audit across core flows.",
        normalized_query_lower="accessibility",
    )


def test_freshness_preset_caps_reflect_spec_table_rule_src_002() -> None:
    """RULE-SRC-002 scenario outline freshness caps."""
    assert freshness_upper_bound_days("last_7_days") == 7
    assert freshness_upper_bound_days("last_30_days") == 30
    assert freshness_upper_bound_days("last_90_days") == 90
    assert freshness_upper_bound_days("all_time") is None


def test_combined_search_and_freshness_uses_logical_and_rule_src_003() -> None:
    """RULE-SRC-003 combines search phrases with freshness window."""
    issues = (
        {"title": "Mobile redesign polish", "body": "", "freshness_days": 3},
        {"title": "Mobile app icons", "body": "Need bitmap exports", "freshness_days": 45},
    )
    narrowed = narrow_issues_for_discovery(
        issues,
        normalized_query_lower="mobile",
        freshness_preset="last_7_days",
    )
    assert narrowed == [{"title": "Mobile redesign polish", "body": "", "freshness_days": 3}]