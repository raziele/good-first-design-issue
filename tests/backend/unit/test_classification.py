"""
Tests for Issue Classification behavior.
Spec: specs/behavior/classification.spec.md
"""
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(title: str = "Design issue", description: str = "Some content", **overrides):
    return {"title": title, "description": description, **overrides}


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestClassificationRelevance:
    """RULE-CLS-001: AI classifies each issue as relevant or not_relevant."""

    def test_classification_design_issue_classified_as_relevant(self):
        """
        Scenario: Design issue is classified as relevant
        Given an issue with title "Create wireframes for settings page"
        And description contains "mockup, user flow, Figma"
        Then the issue is classified as "relevant"
        """
        issue = make_issue(
            title="Create wireframes for settings page",
            description="We need a mockup, user flow, and Figma prototype for this feature.",
        )
        result = _classify(issue)
        assert result["classification"] == "relevant", (
            "Issue with design keywords (mockup, user flow, Figma) must be classified as relevant"
        )

    def test_classification_backend_issue_classified_as_not_relevant(self):
        """
        Scenario: Backend issue is classified as not relevant
        Given an issue with title "Fix API endpoint for user auth"
        And description contains "database, migration, REST API"
        Then the issue is classified as "not_relevant"
        """
        issue = make_issue(
            title="Fix API endpoint for user auth",
            description="Update the database migration and fix the REST API.",
        )
        result = _classify(issue)
        assert result["classification"] == "not_relevant", (
            "Issue with backend keywords (database, migration, REST API) must be classified as not_relevant"
        )


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestClassificationEmptyDescription:
    """RULE-CLS-002: Empty or placeholder-only descriptions → not_relevant."""

    def test_classification_empty_description_is_not_relevant(self):
        """
        Scenario: Empty description
        Given an issue with an empty description field
        Then the issue is classified as "not_relevant"
        """
        issue = make_issue(title="Some design task", description="")
        result = _classify(issue)
        assert result["classification"] == "not_relevant", (
            "Issue with empty description must be classified as not_relevant"
        )

    def test_classification_placeholder_only_description_is_not_relevant(self):
        """
        Scenario: Placeholder-only description
        Given an issue where description contains only headings with no content
        Then the issue is classified as "not_relevant"
        """
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        issue = make_issue(title="Design placeholder", description=placeholder)
        result = _classify(issue)
        assert result["classification"] == "not_relevant", (
            "Issue with only heading placeholders must be classified as not_relevant"
        )

    def test_classification_whitespace_only_description_is_not_relevant(self):
        """Whitespace-only description is treated as empty → not_relevant."""
        issue = make_issue(title="UX task", description="   \n\n\t  ")
        result = _classify(issue)
        assert result["classification"] == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestClassificationClaimedIssues:
    """RULE-CLS-003: Design-relevant claimed issue → relevant + is_claimed = true."""

    def test_classification_claimed_design_issue_flagged_not_downgraded(self):
        """
        Scenario: Claimed issue flagged
        Given a design-relevant issue
        And a comment exists saying "I'm taking this on"
        Then classification = relevant
        And is_claimed = true
        """
        issue = make_issue(
            title="Redesign settings page",
            description="We need a Figma mockup and user flow.",
            comments=["I'm taking this on — will deliver wireframes by Friday."],
        )
        result = _classify_with_comments(issue)
        assert result["classification"] == "relevant", (
            "Claimed design issue must remain classified as relevant"
        )
        assert result["is_claimed"] is True, (
            "Claimed design issue must have is_claimed = true"
        )

    def test_classification_unclaimed_issue_not_flagged(self):
        """Issue without claim-indicating comments must have is_claimed = false."""
        issue = make_issue(
            title="Redesign settings page",
            description="We need a Figma mockup and user flow.",
            comments=["Can you add more details to the acceptance criteria?"],
        )
        result = _classify_with_comments(issue)
        assert result["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

EXCLUSION_PATTERNS = [
    ("test coverage, unit test, QA case", "test coverage: add unit tests for auth module"),
    ("api endpoint, backend, database migration", "migrate database schema for new API endpoint"),
    ("refactor, rename X to Y", "refactor: rename UserController to AccountController"),
    ("implement in code, code base for", "implement in code base for the new auth flow"),
    ("sprite sheet, UTF files, game assets", "update sprite sheet and UTF game asset files"),
]


class TestClassificationExclusions:
    """RULE-CLS-004: Specific categories always classify as not_relevant."""

    @pytest.mark.parametrize("pattern_label,content", EXCLUSION_PATTERNS)
    def test_classification_exclusion_by_category(self, pattern_label, content):
        """
        Scenario Outline: Exclusion by category
        Given an issue with content matching {exclusion_pattern}
        Then the issue is classified as "not_relevant"
        """
        issue = make_issue(title=content, description=content)
        result = _classify(issue)
        assert result["classification"] == "not_relevant", (
            f"Issue matching exclusion pattern '{pattern_label}' must be classified as not_relevant"
        )


# ---------------------------------------------------------------------------
# ClassificationResult entity invariants (ENTITY-003)
# ---------------------------------------------------------------------------

class TestClassificationResultEntity:
    """ClassificationResult must include confidence and reason fields."""

    def test_classification_result_includes_confidence(self):
        """ClassificationResult confidence must be float in [0.0, 1.0]."""
        issue = make_issue(
            title="Design new onboarding flow",
            description="Create mockups and Figma prototype.",
        )
        result = _classify(issue)
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_classification_result_includes_reason(self):
        """ClassificationResult must include a non-empty reason string."""
        issue = make_issue(
            title="Fix database migration",
            description="Update schema to support new API endpoint.",
        )
        result = _classify(issue)
        assert "reason" in result
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _classify(issue: dict) -> dict:
    """
    Stub classifier — returns classification + confidence + reason.
    TODO: replace with real classification agent import.
    """
    description = issue.get("description", "")
    title = issue.get("title", "")
    text = (title + " " + description).lower()

    exclusion_keywords = [
        "unit test", "test coverage", "qa case",
        "api endpoint", "database migration", "backend",
        "refactor", "rename",
        "implement in code", "code base for",
        "sprite sheet", "utf files", "game assets",
    ]
    design_keywords = ["mockup", "user flow", "figma", "wireframe", "ux", "ui", "design", "prototype"]

    stripped = description.strip()
    is_placeholder = _is_placeholder_description(stripped)

    if not stripped or is_placeholder:
        return {"classification": "not_relevant", "confidence": 1.0, "reason": "Empty or placeholder description"}

    for kw in exclusion_keywords:
        if kw in text:
            return {"classification": "not_relevant", "confidence": 0.95, "reason": f"Matched exclusion keyword: {kw}"}

    for kw in design_keywords:
        if kw in text:
            return {"classification": "relevant", "confidence": 0.9, "reason": f"Matched design keyword: {kw}"}

    return {"classification": "not_relevant", "confidence": 0.6, "reason": "No design keywords matched"}


def _classify_with_comments(issue: dict) -> dict:
    """Stub: classify and detect claim status from comments."""
    # TODO: replace with real implementation import
    result = _classify(issue)
    comments = issue.get("comments", [])
    claim_phrases = ["i'm taking", "i'll work on", "claiming this", "taking this on", "i will take"]
    is_claimed = any(
        any(phrase in c.lower() for phrase in claim_phrases)
        for c in comments
    )
    result["is_claimed"] = is_claimed
    return result


def _is_placeholder_description(description: str) -> bool:
    """Return True if description contains only markdown headings with no real content."""
    import re
    stripped = re.sub(r'^#+\s+\w.*$', '', description, flags=re.MULTILINE).strip()
    return len(stripped) == 0
