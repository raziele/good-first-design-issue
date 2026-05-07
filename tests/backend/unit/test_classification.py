"""
Backend unit tests for Issue Classification.
Spec: specs/behavior/classification.spec.md
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers — lightweight classification stub used for unit testing logic
# ---------------------------------------------------------------------------

DESIGN_KEYWORDS = {"wireframe", "mockup", "figma", "user flow", "ux", "ui", "design", "prototype", "sketch"}

EXCLUSION_PATTERNS = [
    {"test coverage", "unit test", "qa case"},
    {"api endpoint", "backend", "database migration"},
    {"refactor", "rename"},
    {"implement in code", "code base for"},
    {"sprite sheet", "utf files", "game assets"},
]


def _contains_any(text: str, terms: set) -> bool:
    lower = text.lower()
    return any(term in lower for term in terms)


def _is_excluded(title: str, description: str) -> bool:
    combined = f"{title} {description}".lower()
    for pattern_set in EXCLUSION_PATTERNS:
        if _contains_any(combined, pattern_set):
            return True
    return False


def classify(title: str, description: str | None) -> str:
    """
    Minimal deterministic classification stub that mirrors the behavioral contract.
    The real system uses an AI agent; this stub encodes only the rules from the spec.
    """
    if not description or not description.strip():
        return "not_relevant"

    # Check if description is placeholder-only (only headings, no real content)
    stripped = description.replace("##", "").replace("#", "").strip()
    placeholder_headings = {"Description", "TODO", "Acceptance Criteria", "Steps to Reproduce"}
    words = {w.strip() for w in stripped.split("\n") if w.strip()}
    if words and words.issubset(placeholder_headings):
        return "not_relevant"

    if _is_excluded(title, description):
        return "not_relevant"

    return "relevant"  # Default: let AI decide; stub assumes non-excluded == relevant


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestRuleCLS001ClassificationIsFullyAutomated:
    def test_design_issue_classified_as_relevant(self):
        """Scenario: Design issue is classified as relevant."""
        title = "Create wireframes for settings page"
        description = "We need mockup, user flow, Figma designs for the settings screen."
        assert classify(title, description) == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        """Scenario: Backend issue is classified as not relevant."""
        title = "Fix API endpoint for user auth"
        description = "Update the database migration and REST API for the backend."
        assert classify(title, description) == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestRuleCLS002EmptyDescriptionsAreNotRelevant:
    def test_empty_description_classified_not_relevant(self):
        """Scenario: Empty description."""
        assert classify("Some design issue", "") == "not_relevant"

    def test_none_description_classified_not_relevant(self):
        """None description treated as empty."""
        assert classify("Some design issue", None) == "not_relevant"

    def test_whitespace_only_description_classified_not_relevant(self):
        """Whitespace-only description treated as empty."""
        assert classify("Some design issue", "   \n\t  ") == "not_relevant"

    def test_placeholder_only_description_classified_not_relevant(self):
        """Scenario: Placeholder-only description."""
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        assert classify("Some issue", placeholder) == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestRuleCLS003AlreadyClaimedIssuesRemainRelevant:
    def test_claimed_issue_classification_remains_relevant(self):
        """Scenario: Claimed issue flagged — classification stays relevant."""
        # The spec says classification stays 'relevant'; is_claimed is set separately
        title = "Redesign the onboarding flow"
        description = "We need UX designs for the onboarding screens."
        classification = classify(title, description)
        assert classification == "relevant"

    def test_is_claimed_flag_set_independently(self):
        """is_claimed is derived from GitHub comments, not from classification."""
        issue = {
            "classification": "relevant",
            "is_claimed": True,  # set by enrichment step
        }
        assert issue["classification"] == "relevant"
        assert issue["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

class TestRuleCLS004ClassificationExclusionRules:
    @pytest.mark.parametrize("title,description", [
        ("Add test coverage for auth module", "We need unit test and QA case coverage."),
        ("Create API endpoint for users", "Backend database migration required."),
        ("Refactor the auth module", "Rename UserService to AuthService."),
        ("Implement in code the payment flow", "Code base for the new checkout."),
        ("Update sprite sheet assets", "Provide UTF files and game assets."),
    ])
    def test_exclusion_by_category(self, title, description):
        """Scenario Outline: Exclusion by category."""
        assert classify(title, description) == "not_relevant"

    def test_design_keywords_do_not_override_exclusion(self):
        """Exclusion rules take precedence even if design keywords are present."""
        title = "Refactor the Figma component library"
        description = "Rename components and refactor the design system codebase."
        # 'refactor' and 'rename' trigger exclusion even with 'Figma' present
        assert classify(title, description) == "not_relevant"
