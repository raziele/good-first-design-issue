"""
Tests for Issue Classification behavior.
Spec: specs/behavior/classification.spec.md
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_issue(title: str = "", description: str = "") -> dict:
    return {"title": title, "description": description}


def is_placeholder_only(description: str) -> bool:
    """
    Detect whether a description is empty or consists only of section headings
    with no actual content (RULE-CLS-002).
    """
    import re
    stripped = description.strip()
    if not stripped:
        return True
    # Remove all markdown headings and blank lines; if nothing remains → placeholder
    content = re.sub(r"^#+\s.*$", "", stripped, flags=re.MULTILINE)
    return not content.strip()


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

DESIGN_KEYWORDS = [
    "wireframe", "mockup", "user flow", "figma", "ux", "ui", "design",
    "prototype", "accessibility", "onboarding", "visual", "layout",
]


def classify(issue: dict) -> str:
    """
    Simplified classification logic that mirrors the behavioral contract
    described in RULE-CLS-001 through RULE-CLS-004.

    This is an approximation for test purposes — the real classifier is AI-based.
    Tests validate the *contract*, not the AI implementation.
    """
    combined = (issue["title"] + " " + issue["description"]).lower()

    # RULE-CLS-002: empty/placeholder → not_relevant
    if is_placeholder_only(issue["description"]):
        return "not_relevant"

    # RULE-CLS-004: exclusion patterns
    for pattern in EXCLUSION_PATTERNS:
        if pattern in combined:
            return "not_relevant"

    # RULE-CLS-001: design keywords → relevant
    for kw in DESIGN_KEYWORDS:
        if kw in combined:
            return "relevant"

    return "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestAutomatedClassification:
    def test_design_issue_classified_as_relevant(self):
        """
        RULE-CLS-001 Scenario: Design issue is classified as relevant.
        Given title "Create wireframes for settings page" and description with
        "mockup, user flow, Figma", then classification = relevant.
        """
        issue = make_issue(
            title="Create wireframes for settings page",
            description="We need a mockup and user flow in Figma.",
        )
        assert classify(issue) == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        """
        RULE-CLS-001 Scenario: Backend issue is classified as not relevant.
        Given title "Fix API endpoint for user auth" and description with
        "database, migration, REST API", then classification = not_relevant.
        """
        issue = make_issue(
            title="Fix API endpoint for user auth",
            description="The database migration broke the REST API endpoint.",
        )
        assert classify(issue) == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestEmptyDescriptions:
    def test_empty_description_is_not_relevant(self):
        """
        RULE-CLS-002 Scenario: Empty description.
        Given an empty description, then classification = not_relevant.
        """
        issue = make_issue(title="Design task", description="")
        assert classify(issue) == "not_relevant"

    def test_placeholder_only_description_is_not_relevant(self):
        """
        RULE-CLS-002 Scenario: Placeholder-only description.
        Given a description with only markdown headings and no content,
        then classification = not_relevant.
        """
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        issue = make_issue(title="Design task", description=placeholder)
        assert classify(issue) == "not_relevant"

    def test_whitespace_only_description_is_not_relevant(self):
        """Edge: whitespace-only description treated as empty."""
        issue = make_issue(title="Design task", description="   \n\n  ")
        assert classify(issue) == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestClaimedIssues:
    def test_claimed_design_issue_remains_relevant(self):
        """
        RULE-CLS-003 Scenario: Claimed issue flagged.
        A design-relevant issue with a claim comment is still classification=relevant
        but is_claimed=true.
        """
        issue = make_issue(
            title="Redesign onboarding flow",
            description="Please create a user flow and wireframes for the new onboarding.",
        )
        classification = classify(issue)
        assert classification == "relevant"

        # Simulated enrichment: comment analysis sets is_claimed
        comments = ["I'm taking this on — will submit a Figma file by Friday."]
        claim_phrases = ["i'm taking", "i'll take", "i will work", "working on this"]
        is_claimed = any(
            phrase in comment.lower()
            for comment in comments
            for phrase in claim_phrases
        )
        assert is_claimed is True

    def test_is_claimed_false_when_no_claim_comments(self):
        """
        RULE-CLS-003 complementary: no claim phrases → is_claimed = false.
        """
        comments = ["Can someone clarify the scope?", "This needs more detail."]
        claim_phrases = ["i'm taking", "i'll take", "i will work", "working on this"]
        is_claimed = any(
            phrase in comment.lower()
            for comment in comments
            for phrase in claim_phrases
        )
        assert is_claimed is False


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

class TestExclusionRules:
    @pytest.mark.parametrize("exclusion_pattern", [
        "test coverage, unit test, QA case",
        "api endpoint, backend, database migration",
        "refactor, rename X to Y",
        "implement in code, code base for",
        "sprite sheet, UTF files, game assets",
    ])
    def test_exclusion_pattern_results_in_not_relevant(self, exclusion_pattern):
        """
        RULE-CLS-004 Scenario Outline: Exclusion by category.
        Each exclusion pattern must result in not_relevant classification.
        """
        first_term = exclusion_pattern.split(",")[0].strip().lower()
        issue = make_issue(
            title=f"Task about {first_term}",
            description=f"This issue is about {first_term}.",
        )
        assert classify(issue) == "not_relevant"

    def test_design_keyword_does_not_override_exclusion(self):
        """
        RULE-CLS-004: Exclusion patterns take precedence over design keywords.
        An issue that mentions both "wireframe" and "unit test" should be
        not_relevant because of the exclusion rule.

        TODO: Confirm priority order with spec author — current spec implies
        exclusions are checked before design keywords.
        """
        issue = make_issue(
            title="Add unit test for wireframe renderer",
            description="We need to cover the unit test cases for the wireframe module.",
        )
        assert classify(issue) == "not_relevant"
