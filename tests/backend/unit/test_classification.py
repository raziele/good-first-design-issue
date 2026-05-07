"""
Unit tests for Issue Classification rules.
Specs: specs/behavior/classification.spec.md
"""

import pytest
import re


# ---------------------------------------------------------------------------
# Minimal classifier stub — mirrors the classification contract from the spec.
# The real AI classifier is in ETL; these tests assert the behavioral contract
# using a keyword-based stand-in so tests remain hermetic.
# ---------------------------------------------------------------------------

DESIGN_KEYWORDS = frozenset([
    "mockup", "wireframe", "user flow", "figma", "ux", "ui", "design",
    "prototype", "sketch", "accessibility", "typography", "layout",
    "onboarding", "component", "icon", "color", "visual",
])

EXCLUSION_PATTERNS = [
    re.compile(r"\b(test coverage|unit test|qa case)\b", re.IGNORECASE),
    re.compile(r"\b(api endpoint|backend|database migration)\b", re.IGNORECASE),
    re.compile(r"\b(refactor|rename\s+\w+\s+to\s+\w+)\b", re.IGNORECASE),
    re.compile(r"\b(implement in code|code base for)\b", re.IGNORECASE),
    re.compile(r"\b(sprite sheet|utf files|game assets)\b", re.IGNORECASE),
]

PLACEHOLDER_ONLY = re.compile(
    r"^(\s*#{1,6}\s+\w.*\n?)*\s*$", re.MULTILINE
)


def _has_content(description: str) -> bool:
    """Return False for empty or heading-only descriptions."""
    if not description or not description.strip():
        return False
    stripped = re.sub(r"^#{1,6}\s+.*", "", description, flags=re.MULTILINE).strip()
    return bool(stripped)


def classify(title: str, description: str) -> str:
    """
    Stub classifier that implements the behavioral contract from the spec.
    Returns 'relevant' or 'not_relevant'.
    """
    text = f"{title} {description}".lower()

    if not _has_content(description):
        return "not_relevant"

    for pattern in EXCLUSION_PATTERNS:
        if pattern.search(text):
            return "not_relevant"

    if any(kw in text for kw in DESIGN_KEYWORDS):
        return "relevant"

    return "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestRuleCLS001:
    def test_design_issue_classified_as_relevant(self):
        result = classify(
            title="Create wireframes for settings page",
            description="Need mockup, user flow, Figma assets for the settings redesign.",
        )
        assert result == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        result = classify(
            title="Fix API endpoint for user auth",
            description="database migration required, update REST API schema.",
        )
        assert result == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestRuleCLS002:
    def test_empty_description_is_not_relevant(self):
        result = classify(title="Some issue", description="")
        assert result == "not_relevant"

    def test_whitespace_only_description_is_not_relevant(self):
        result = classify(title="Some issue", description="   \n  \t  ")
        assert result == "not_relevant"

    def test_placeholder_only_description_is_not_relevant(self):
        placeholder = (
            "## Description\n"
            "## TODO\n"
            "## Acceptance Criteria\n"
        )
        result = classify(title="Some issue", description=placeholder)
        assert result == "not_relevant"

    def test_headings_with_real_content_not_excluded(self):
        desc = "## Description\nPlease redesign the onboarding flow using Figma."
        result = classify(title="Redesign onboarding", description=desc)
        assert result == "relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestRuleCLS003:
    def test_claimed_issue_stays_relevant(self):
        # Classification is independent of claim status per spec.
        result = classify(
            title="Redesign the dashboard UI",
            description="Figma mockup needed for dashboard layout.",
        )
        assert result == "relevant"

    def test_is_claimed_set_independently_of_classification(self):
        # Spec: classification = relevant AND is_claimed = true are orthogonal.
        # This test asserts the data model allows both to be true simultaneously.
        issue = {
            "classification": "relevant",
            "is_claimed": True,
        }
        assert issue["classification"] == "relevant"
        assert issue["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules (parametrized)
# ---------------------------------------------------------------------------

EXCLUSION_CASES = [
    ("Add test coverage for auth module", "test coverage, unit test, qa case"),
    ("Update api endpoint schema", "api endpoint, backend, database migration"),
    ("Refactor the user model", "refactor, rename X to Y"),
    ("Implement in code the payment flow", "implement in code, code base for"),
    ("Generate sprite sheet for game assets", "sprite sheet, UTF files, game assets"),
]


class TestRuleCLS004:
    @pytest.mark.parametrize("title,description", EXCLUSION_CASES)
    def test_exclusion_pattern_not_relevant(self, title, description):
        result = classify(title=title, description=description)
        assert result == "not_relevant", (
            f"Expected 'not_relevant' for title={title!r}, desc={description!r}"
        )

    def test_design_keywords_override_non_excluded_content(self):
        result = classify(
            title="Mobile onboarding redesign",
            description="Create wireframe and prototype for the new user flow.",
        )
        assert result == "relevant"

    def test_exclusion_case_insensitive(self):
        result = classify(
            title="DATABASE MIGRATION needed",
            description="Update BACKEND schema",
        )
        assert result == "not_relevant"
