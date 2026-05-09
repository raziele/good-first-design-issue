"""
Tests for Issue Classification rules.
RULE-CLS-001: Classification is fully automated
RULE-CLS-002: Empty descriptions are not relevant
RULE-CLS-003: Already-claimed issues remain relevant but flagged
RULE-CLS-004: Classification exclusion rules
"""

import pytest
from app.classification import classify_issue, EXCLUSION_PATTERNS


class TestRuleCLS001AutomatedClassification:
    """RULE-CLS-001: Classification is fully automated."""

    def test_design_issue_classified_as_relevant(self):
        """Design issue with UX/UI keywords classifies as relevant."""
        result = classify_issue(
            title="Create wireframes for settings page",
            description="We need a mockup, user flow, and Figma prototype for the settings page redesign.",
        )
        assert result.classification == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        """Backend/engineering issue classifies as not_relevant."""
        result = classify_issue(
            title="Fix API endpoint for user auth",
            description="The database migration for the REST API is broken. Needs backend fix.",
        )
        assert result.classification == "not_relevant"


class TestRuleCLS002EmptyDescriptions:
    """RULE-CLS-002: Empty descriptions are not relevant."""

    def test_empty_description_is_not_relevant(self):
        """Issue with empty description body classifies as not_relevant."""
        result = classify_issue(
            title="Some design task",
            description="",
        )
        assert result.classification == "not_relevant"

    def test_placeholder_only_description_is_not_relevant(self):
        """Issue with only section headings and no content classifies as not_relevant."""
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        result = classify_issue(
            title="Some design task",
            description=placeholder,
        )
        assert result.classification == "not_relevant"


class TestRuleCLS003ClaimedIssuesRemainRelevant:
    """RULE-CLS-003: Already-claimed issues remain relevant but flagged."""

    def test_claimed_design_issue_is_still_relevant_but_flagged(self):
        """A design-relevant issue with a claim comment stays relevant with is_claimed=True."""
        result = classify_issue(
            title="Redesign the onboarding flow",
            description="We need a full UX audit and new wireframes for onboarding.",
            comments=["I'm taking this on — expect a design update soon."],
        )
        assert result.classification == "relevant"
        assert result.is_claimed is True


class TestRuleCLS004ExclusionRules:
    """RULE-CLS-004: Classification exclusion rules — specific patterns auto-classify as not_relevant."""

    @pytest.mark.parametrize(
        "exclusion_text",
        [
            "test coverage, unit test, QA case",
            "api endpoint, backend, database migration",
            "refactor, rename X to Y",
            "implement in code, code base for",
            "sprite sheet, UTF files, game assets",
        ],
    )
    def test_exclusion_pattern_classifies_as_not_relevant(self, exclusion_text):
        """Issues matching exclusion patterns are classified as not_relevant."""
        result = classify_issue(
            title="Task",
            description=exclusion_text,
        )
        assert result.classification == "not_relevant"

    def test_exclusion_patterns_constant_exists(self):
        """EXCLUSION_PATTERNS constant exists and is non-empty."""
        assert EXCLUSION_PATTERNS, "EXCLUSION_PATTERNS must be non-empty"
        assert isinstance(EXCLUSION_PATTERNS, (set, frozenset, list, tuple))
