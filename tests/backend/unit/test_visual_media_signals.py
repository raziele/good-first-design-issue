"""Regression tests for LEVEL8 RULE-ETL-006 (media cues on Issue bodies)."""

from __future__ import annotations

import pytest

from app.issue_media_signals import markdown_body_has_linked_visual_anchor


@pytest.mark.parametrize(
    ("body", "expects_signal"),
    [
        ('See ![screenshot](https://cdn.example.org/preview.png)', True),
        ("Plain copy without URLs or uploads.", False),
    ],
)
def test_media_presence_reflects_linked_assets_rule_etl_006(body: str, expects_signal: bool) -> None:
    """RULE-ETL-006 scenarios for linked Issue media."""
    assert markdown_body_has_linked_visual_anchor(body) is expects_signal


def test_linked_media_without_visual_tokens_is_ambiguous_skip() -> None:
    """TODO: ambiguity between hyperlink-only mentions vs explicit media RULE-ETL-006."""
    pytest.skip("Spec lists external links broadly; deterministic signal not defined in behavior spec.")
