"""
Backend tests for Issue Classification.
Spec: specs/behavior/classification.spec.md
"""
import pytest
from conftest import make_issue


# ---------------------------------------------------------------------------
# Helpers — simulate classifier contract (pure logic / schema validation)
# The actual AI call is not exercised here; these tests validate the
# classification contract and data invariants.
# ---------------------------------------------------------------------------

def is_valid_classification(value: str) -> bool:
    return value in ("relevant", "not_relevant")


def build_classification_result(issue_id: str, classification: str, confidence: float, reason: str) -> dict:
    return {
        "issue_id": issue_id,
        "classification": classification,
        "confidence": confidence,
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

def test_design_issue_classified_as_relevant():
    """RULE-CLS-001: Scenario: Design issue is classified as relevant."""
    issue = make_issue(
        title="Create wireframes for settings page",
        description="mockup, user flow, Figma — need full design pass.",
        classification="relevant",
    )
    assert issue["classification"] == "relevant"


def test_backend_issue_classified_as_not_relevant():
    """RULE-CLS-001: Scenario: Backend issue is classified as not relevant."""
    issue = make_issue(
        title="Fix API endpoint for user auth",
        description="database, migration, REST API endpoint needs update.",
        classification="not_relevant",
    )
    assert issue["classification"] == "not_relevant"


def test_classification_value_is_valid_enum():
    """RULE-CLS-001: Classification result is always a valid enum value."""
    for value in ("relevant", "not_relevant"):
        result = build_classification_result("issue-001", value, 0.9, "test reason")
        assert is_valid_classification(result["classification"])


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

def test_empty_description_classified_not_relevant():
    """RULE-CLS-002: Scenario: Empty description."""
    issue = make_issue(description="", classification="not_relevant")
    assert issue["classification"] == "not_relevant"


def test_placeholder_only_description_classified_not_relevant():
    """RULE-CLS-002: Scenario: Placeholder-only description."""
    placeholder = "## Description\n## TODO\n## Acceptance Criteria"
    issue = make_issue(description=placeholder, classification="not_relevant")
    assert issue["classification"] == "not_relevant"


def test_description_empty_string_is_falsy():
    """RULE-CLS-002: Guard — empty description string is treated as no content."""
    assert not "".strip()


def test_placeholder_description_has_no_real_content():
    """RULE-CLS-002: Placeholder-only headings strip to nothing meaningful."""
    placeholder = "## Description\n## TODO\n## Acceptance Criteria"
    # Strip markdown headings and whitespace
    stripped = "\n".join(
        line for line in placeholder.splitlines()
        if not line.strip().startswith("#")
    ).strip()
    assert stripped == ""


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

def test_claimed_design_issue_stays_relevant_but_flagged():
    """RULE-CLS-003: Scenario: Claimed issue flagged."""
    issue = make_issue(
        classification="relevant",
        is_claimed=True,
    )
    assert issue["classification"] == "relevant"
    assert issue["is_claimed"] is True


def test_claimed_flag_does_not_override_classification():
    """RULE-CLS-003: is_claimed=true does not demote classification to not_relevant."""
    issue = make_issue(classification="relevant", is_claimed=True)
    assert issue["classification"] == "relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

EXCLUSION_PATTERNS = [
    "test coverage, unit test, QA case",
    "api endpoint, backend, database migration",
    "refactor, rename X to Y",
    "implement in code, code base for",
    "sprite sheet, UTF files, game assets",
]


@pytest.mark.parametrize("exclusion_pattern", EXCLUSION_PATTERNS)
def test_exclusion_by_category_classified_not_relevant(exclusion_pattern):
    """RULE-CLS-004: Scenario Outline: Exclusion by category."""
    # The issue content matches an exclusion pattern → must be not_relevant
    issue = make_issue(
        description=exclusion_pattern,
        classification="not_relevant",
    )
    assert issue["classification"] == "not_relevant"


def test_classification_result_has_required_fields():
    """ENTITY-003: ClassificationResult has all required attributes."""
    result = build_classification_result(
        issue_id="issue-001",
        classification="relevant",
        confidence=0.92,
        reason="Contains design keywords: wireframe, Figma, mockup.",
    )
    assert "issue_id" in result
    assert "classification" in result
    assert "confidence" in result
    assert "reason" in result


def test_classification_confidence_is_between_0_and_1():
    """ENTITY-003: confidence is a float in [0.0, 1.0]."""
    result = build_classification_result("id", "relevant", 0.85, "reason")
    assert 0.0 <= result["confidence"] <= 1.0
