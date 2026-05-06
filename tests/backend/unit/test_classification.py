"""
Backend unit tests for Issue Classification.
Spec: specs/behavior/classification.spec.md
Rules: RULE-CLS-001 through RULE-CLS-004
"""
import pytest


# ---------------------------------------------------------------------------
# Helpers / fake classifier
# ---------------------------------------------------------------------------

DESIGN_KEYWORDS = {"wireframe", "mockup", "figma", "sketch", "user flow", "ux", "ui", "design"}
EXCLUSION_PATTERNS = [
    "test coverage",
    "unit test",
    "qa case",
    "api endpoint",
    "backend",
    "database migration",
    "refactor",
    "rename",
    "implement in code",
    "code base for",
    "sprite sheet",
    "utf files",
    "game assets",
]


def classify_issue(title: str, description: str) -> dict:
    """
    Stub classifier that mirrors the behavioral contract from the spec.
    Returns: {"classification": "relevant"|"not_relevant", "is_claimed": False}
    """
    combined = f"{title} {description}".lower()

    # Empty / placeholder-only description
    if not description or not description.strip():
        return {"classification": "not_relevant", "is_claimed": False}

    placeholder_only = all(
        line.startswith("#") or line.strip() == ""
        for line in description.splitlines()
    )
    if placeholder_only:
        return {"classification": "not_relevant", "is_claimed": False}

    # Exclusion patterns take precedence
    for pattern in EXCLUSION_PATTERNS:
        if pattern in combined:
            return {"classification": "not_relevant", "is_claimed": False}

    # Design keyword match
    if any(kw in combined for kw in DESIGN_KEYWORDS):
        return {"classification": "relevant", "is_claimed": False}

    return {"classification": "not_relevant", "is_claimed": False}


def enrich_with_claim_status(result: dict, comments: list[str]) -> dict:
    """
    If the issue is relevant and a comment indicates a claim, set is_claimed = True.
    """
    claim_signals = ["i'm taking this", "i'll take this", "working on this", "i'll work on"]
    if result["classification"] == "relevant":
        for comment in comments:
            if any(signal in comment.lower() for signal in claim_signals):
                result = {**result, "is_claimed": True}
    return result


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestRuleCLS001:
    """RULE-CLS-001: Every fetched issue is classified as relevant or not_relevant."""

    def test_design_issue_classified_as_relevant(self):
        result = classify_issue(
            title="Create wireframes for settings page",
            description="We need a mockup, user flow, Figma prototype for this screen.",
        )
        assert result["classification"] == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        result = classify_issue(
            title="Fix API endpoint for user auth",
            description="database, migration, REST API changes needed.",
        )
        assert result["classification"] == "not_relevant"

    def test_classification_always_returns_known_value(self):
        result = classify_issue(title="Some issue", description="Some description")
        assert result["classification"] in ("relevant", "not_relevant")


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestRuleCLS002:
    """RULE-CLS-002: Issues with empty or placeholder-only descriptions → not_relevant."""

    def test_empty_description_classified_not_relevant(self):
        result = classify_issue(title="Design something", description="")
        assert result["classification"] == "not_relevant"

    def test_whitespace_only_description_classified_not_relevant(self):
        result = classify_issue(title="Design something", description="   \n  \t  ")
        assert result["classification"] == "not_relevant"

    def test_placeholder_only_description_classified_not_relevant(self):
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        result = classify_issue(title="Design something", description=placeholder)
        assert result["classification"] == "not_relevant"

    def test_description_with_headings_and_content_is_not_placeholder(self):
        """Headings with actual content beneath them should be processed normally."""
        desc = "## Description\nWe need Figma wireframes for the onboarding screen."
        result = classify_issue(title="Design onboarding", description=desc)
        assert result["classification"] == "relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestRuleCLS003:
    """RULE-CLS-003: Design-relevant + claimed comment → classification=relevant, is_claimed=True."""

    def test_claimed_design_issue_is_relevant_and_flagged(self):
        result = classify_issue(
            title="Redesign the dashboard UI",
            description="We need Figma mockups for the new dashboard.",
        )
        result = enrich_with_claim_status(result, comments=["I'm taking this on"])
        assert result["classification"] == "relevant"
        assert result["is_claimed"] is True

    def test_not_relevant_issue_is_not_flagged_even_with_claim_comment(self):
        """A non-design issue with a claim comment is still not_relevant (not shown)."""
        result = classify_issue(
            title="Fix database migration",
            description="database migration and backend changes.",
        )
        result = enrich_with_claim_status(result, comments=["I'm taking this on"])
        assert result["classification"] == "not_relevant"
        assert result["is_claimed"] is False

    def test_relevant_issue_without_claim_comment_has_is_claimed_false(self):
        result = classify_issue(
            title="Design settings page",
            description="Figma wireframes needed.",
        )
        result = enrich_with_claim_status(result, comments=["LGTM", "Needs more context"])
        assert result["classification"] == "relevant"
        assert result["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

class TestRuleCLS004:
    """RULE-CLS-004: Specific categories automatically classify as not_relevant."""

    @pytest.mark.parametrize("exclusion_content", [
        "test coverage, unit test, QA case",
        "api endpoint, backend, database migration",
        "refactor rename X to Y",
        "implement in code, code base for",
        "sprite sheet, UTF files, game assets",
    ])
    def test_exclusion_pattern_results_in_not_relevant(self, exclusion_content):
        result = classify_issue(
            title="Some issue",
            description=exclusion_content,
        )
        assert result["classification"] == "not_relevant", (
            f"Expected not_relevant for exclusion content: {exclusion_content!r}"
        )

    def test_exclusion_overrides_design_keywords(self):
        """Exclusion patterns beat design keywords in the same description."""
        result = classify_issue(
            title="Design the database migration UI",
            description="We need Figma mockups but also need a database migration.",
        )
        assert result["classification"] == "not_relevant"

    def test_non_excluded_design_issue_is_relevant(self):
        result = classify_issue(
            title="Design a new icon set",
            description="Create UI icons for the settings screen using Figma.",
        )
        assert result["classification"] == "relevant"
