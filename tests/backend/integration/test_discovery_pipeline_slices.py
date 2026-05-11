"""Cross-module LEVEL8 regression wiring discovery filters + freshness sort."""

from __future__ import annotations

from app.issue_discovery_filters import narrow_issues_for_discovery

from app.issue_sorting import order_issues_for_homepage


def test_discovery_orders_mobile_slice_for_last_seven_days() -> None:
    """RULE-SRC-003 + RULE-ISS-005 cooperate on browse payloads."""
    pool = (
        {"id": "a", "title": "Mobile redesign", "body": "", "freshness_days": 3},
        {"id": "b", "title": "Mobile app icons backlog", "body": "", "freshness_days": 9},
        {"id": "c", "title": "Infrastructure costs", "body": "", "freshness_days": 1},
    )
    narrowed = narrow_issues_for_discovery(
        pool,
        normalized_query_lower="mobile",
        freshness_preset="last_7_days",
    )
    chronology = tuple(item["id"] for item in order_issues_for_homepage(narrowed))
    assert chronology == ("a", "b")


def test_discovery_applies_preset_before_sorting_signals() -> None:
    dataset = (
        {"id": "x", "title": "tablet shell", "body": "", "freshness_days": 2},
        {"id": "y", "title": "tablet stylus", "body": "", "freshness_days": 80},
        {"id": "z", "title": "phone shell", "body": "", "freshness_days": 5},
    )
    hits = narrow_issues_for_discovery(dataset, normalized_query_lower="tablet", freshness_preset="last_30_days")
    assert [row["title"] for row in order_issues_for_homepage(hits)] == ["tablet shell", "tablet stylus"]
