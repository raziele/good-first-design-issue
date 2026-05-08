"""Tests for RULE-CLS-001 through RULE-CLS-004: Issue Classification."""
import pytest
from app.classification import classify_issue, DESIGN_KEYWORDS, EXCLUSION_PATTERNS


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

def test_classification_design_issue_is_relevant(design_issue_raw):
    """RULE-CLS-001 — design issue with relevant keywords → relevant."""
    result = classify_issue(design_issue_raw)
    assert result.classification == "relevant"


def test_classification_backend_issue_is_not_relevant(backend_issue_raw):
    """RULE-CLS-001 — backend issue with no design keywords → not_relevant."""
    result = classify_issue(backend_issue_raw)
    assert result.classification == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

def test_classification_empty_description_is_not_relevant():
    """RULE-CLS-002 — issue with empty description → not_relevant."""
    issue = {
        "id": "github_10",
        "title": "Some issue",
        "body": "",
        "html_url": "https://github.com/owner/repo/issues/10",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [],
    }
    result = classify_issue(issue)
    assert result.classification == "not_relevant"


def test_classification_placeholder_only_description_is_not_relevant():
    """RULE-CLS-002 — issue with placeholder-only description → not_relevant."""
    placeholder_body = "## Description\n\n## TODO\n\n## Acceptance Criteria\n"
    issue = {
        "id": "github_11",
        "title": "Feature request",
        "body": placeholder_body,
        "html_url": "https://github.com/owner/repo/issues/11",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [],
    }
    result = classify_issue(issue)
    assert result.classification == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

def test_classification_claimed_design_issue_is_relevant_with_flag():
    """RULE-CLS-003 — design issue with a claim comment → relevant + is_claimed."""
    issue = {
        "id": "github_12",
        "title": "Redesign the onboarding flow",
        "body": "We need new wireframes and user flow for onboarding. Figma mockup required.",
        "html_url": "https://github.com/owner/repo/issues/12",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [{"body": "I'm taking this on"}],
    }
    result = classify_issue(issue)
    assert result.classification == "relevant"
    assert result.is_claimed is True


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("exclusion_phrase,title,body", [
    (
        "test coverage",
        "Improve test coverage for auth module",
        "We need more unit test coverage and QA cases for the auth module.",
    ),
    (
        "api endpoint",
        "Add api endpoint for user profile",
        "Implement REST api endpoint for user profile in backend.",
    ),
    (
        "refactor",
        "Refactor the auth service",
        "Rename X to Y and refactor the codebase.",
    ),
    (
        "implement in code",
        "Implement in code the new algorithm",
        "Add code base for the new search algorithm.",
    ),
    (
        "sprite sheet",
        "Add sprite sheet for game characters",
        "Create UTF files and game assets for characters.",
    ),
])
def test_classification_exclusion_patterns_not_relevant(exclusion_phrase, title, body):
    """RULE-CLS-004 — content matching exclusion patterns → not_relevant."""
    issue = {
        "id": "github_20",
        "title": title,
        "body": body,
        "html_url": "https://github.com/owner/repo/issues/20",
        "state": "open",
        "created_at": "2026-04-10T10:00:00Z",
        "updated_at": "2026-04-10T10:00:00Z",
        "comments": [],
    }
    result = classify_issue(issue)
    assert result.classification == "not_relevant", (
        f"Expected not_relevant for exclusion pattern '{exclusion_phrase}'"
    )


def test_design_keywords_constant_is_non_empty():
    """RULE-CLS-001 — DESIGN_KEYWORDS constant must be defined and non-empty."""
    assert DESIGN_KEYWORDS, "DESIGN_KEYWORDS must be a non-empty collection"
    assert len(DESIGN_KEYWORDS) > 0


def test_exclusion_patterns_constant_is_non_empty():
    """RULE-CLS-004 — EXCLUSION_PATTERNS constant must be defined and non-empty."""
    assert EXCLUSION_PATTERNS, "EXCLUSION_PATTERNS must be a non-empty collection"
    assert len(EXCLUSION_PATTERNS) > 0
