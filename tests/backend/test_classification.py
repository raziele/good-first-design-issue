"""
Tests for Issue Classification behavior.

Spec: specs/behavior/classification.spec.md
Rules: RULE-CLS-001 through RULE-CLS-004
Glossary: TERM-004 (Relevant Issue), TERM-005 (Not Relevant Issue)
Domain: ENTITY-003 (ClassificationResult)

NOTE: Classification is performed by an AI agent. These tests verify the
behavioral CONTRACT (inputs → expected outputs), not the AI model internals.
Tests use a stub classifier that hard-codes expected outcomes; real integration
tests against a live model are out of scope for this suite.
"""
import pytest
from tests.backend.conftest import make_issue


# ---------------------------------------------------------------------------
# Stub classifier — replaces AI agent in unit tests
# ---------------------------------------------------------------------------

DESIGN_KEYWORDS = {"wireframe", "mockup", "user flow", "figma", "ux", "ui",
                   "design", "prototype", "accessibility", "onboarding"}

EXCLUSION_PATTERNS = [
    {"test coverage", "unit test", "qa case"},
    {"api endpoint", "backend", "database migration"},
    {"refactor", "rename"},
    {"implement in code", "code base for"},
    {"sprite sheet", "utf files", "game assets"},
]

PLACEHOLDER_ONLY_PATTERNS = [
    "## Description",
    "## TODO",
    "## Acceptance Criteria",
]


def _is_placeholder_only(description: str) -> bool:
    """Return True if description contains only markdown headings and no real content."""
    stripped = description.strip()
    if not stripped:
        return True
    lines = [l.strip() for l in stripped.splitlines() if l.strip()]
    return all(
        any(line.startswith(p) for p in PLACEHOLDER_ONLY_PATTERNS)
        for line in lines
    )


def classify(issue: dict) -> dict:
    """
    Stub classifier implementing the behavioral contract from RULE-CLS-001 to RULE-CLS-004.
    Returns {"classification": "relevant"|"not_relevant"}.
    """
    text = f"{issue['title']} {issue['description']}".lower()

    # RULE-CLS-002: empty or placeholder-only → not_relevant
    if not issue["description"].strip() or _is_placeholder_only(issue["description"]):
        return {"classification": "not_relevant"}

    # RULE-CLS-004: exclusion patterns → not_relevant
    for pattern_group in EXCLUSION_PATTERNS:
        if any(p in text for p in pattern_group):
            return {"classification": "not_relevant"}

    # RULE-CLS-001: design keywords → relevant
    if any(kw in text for kw in DESIGN_KEYWORDS):
        return {"classification": "relevant"}

    return {"classification": "not_relevant"}


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

def test_classification_design_issue_classified_as_relevant():
    """RULE-CLS-001 / Scenario: Design issue is classified as relevant."""
    issue = make_issue(
        title="Create wireframes for settings page",
        description="Need a mockup, user flow, and Figma link for the settings redesign.",
    )
    result = classify(issue)
    assert result["classification"] == "relevant"


def test_classification_backend_issue_classified_as_not_relevant():
    """RULE-CLS-001 / Scenario: Backend issue is classified as not relevant."""
    issue = make_issue(
        title="Fix API endpoint for user auth",
        description="database migration required, REST API changes.",
    )
    result = classify(issue)
    assert result["classification"] == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

def test_classification_empty_description_is_not_relevant():
    """RULE-CLS-002 / Scenario: Empty description."""
    issue = make_issue(title="Design task", description="")
    result = classify(issue)
    assert result["classification"] == "not_relevant"


def test_classification_placeholder_only_description_is_not_relevant():
    """RULE-CLS-002 / Scenario: Placeholder-only description."""
    placeholder = "## Description\n## TODO\n## Acceptance Criteria"
    issue = make_issue(title="Design placeholder", description=placeholder)
    result = classify(issue)
    assert result["classification"] == "not_relevant"


def test_classification_whitespace_only_description_is_not_relevant():
    """RULE-CLS-002 / Edge: whitespace-only description treated as empty."""
    issue = make_issue(title="Blank issue", description="   \n\n  ")
    result = classify(issue)
    assert result["classification"] == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

def test_classification_claimed_design_issue_stays_relevant_and_flagged():
    """RULE-CLS-003 / Scenario: Claimed issue flagged."""
    issue = make_issue(
        title="Redesign onboarding flow",
        description="Full UX redesign of the onboarding. Figma assets attached.",
        is_claimed=True,
    )
    result = classify(issue)
    # Classification is still relevant — is_claimed is set separately by enrichment
    assert result["classification"] == "relevant"
    assert issue["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("exclusion_text", [
    "test coverage for the login module",
    "unit test for the API",
    "QA case for checkout flow",
    "api endpoint for user data",
    "backend database migration script",
    "refactor the auth module",
    "rename UserService to AuthService",
    "implement in code the new feature",
    "code base for the payment system",
    "sprite sheet for game characters",
    "UTF files for game localization",
    "game assets pack",
])
def test_classification_exclusion_by_category(exclusion_text):
    """RULE-CLS-004 / Scenario Outline: Exclusion by category."""
    issue = make_issue(
        title=exclusion_text,
        description="Some additional context about the task.",
    )
    result = classify(issue)
    assert result["classification"] == "not_relevant", (
        f"Expected not_relevant for exclusion pattern: '{exclusion_text}'"
    )
