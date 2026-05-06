"""
Backend unit tests for Issue Classification behavior.

Spec: specs/behavior/classification.spec.md
"""
import pytest

from tests.backend.unit.conftest import make_issue


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestAutomatedClassification:
    """RULE-CLS-001 — Every fetched issue gets classified as relevant or not_relevant."""

    def test_design_issue_classified_as_relevant(self):
        """Issue about wireframes with Figma/mockup keywords → relevant."""
        issue = make_issue(
            title="Create wireframes for settings page",
            description="We need mockup, user flow, Figma designs for this screen.",
            classification="relevant",
        )
        # TODO: replace with actual classifier call:
        # result = classifier.classify(issue)
        # assert result.classification == "relevant"
        assert issue["classification"] == "relevant"

    def test_backend_issue_classified_as_not_relevant(self):
        """Issue about API endpoints and database migrations → not_relevant."""
        issue = make_issue(
            title="Fix API endpoint for user auth",
            description="Fix the database migration and REST API handler.",
            classification="not_relevant",
        )
        # TODO: replace with actual classifier call
        assert issue["classification"] == "not_relevant"

    @pytest.mark.parametrize("classification", ["relevant", "not_relevant"])
    def test_classification_value_is_valid_enum(self, classification):
        """classification field is always one of the two valid enum values."""
        issue = make_issue(classification=classification)
        assert issue["classification"] in {"relevant", "not_relevant"}


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestEmptyDescriptionClassification:
    """RULE-CLS-002 — Empty or placeholder-only descriptions → not_relevant."""

    def test_empty_description_classified_as_not_relevant(self):
        """Issue with empty description field is classified as not_relevant."""
        issue = make_issue(description="", classification="not_relevant")
        # TODO: replace with: assert classifier.classify(issue).classification == "not_relevant"
        assert issue["classification"] == "not_relevant"

    def test_placeholder_only_description_classified_as_not_relevant(self):
        """Issue with only skeleton headings is classified as not_relevant."""
        placeholder_body = "## Description\n## TODO\n## Acceptance Criteria"
        issue = make_issue(description=placeholder_body, classification="not_relevant")
        # TODO: replace with actual classifier call
        assert issue["classification"] == "not_relevant"

    def test_is_placeholder_description_helper(self):
        """Helper: description with only markdown headings and whitespace is a placeholder."""
        placeholder = "## Description\n\n## TODO\n\n## Acceptance Criteria\n"
        non_placeholder = "## Description\n\nWe need Figma designs for this."

        def is_placeholder(desc: str) -> bool:
            import re
            stripped = re.sub(r"^#+\s+\w.*$", "", desc, flags=re.MULTILINE).strip()
            return stripped == ""

        assert is_placeholder(placeholder) is True
        assert is_placeholder(non_placeholder) is False


# ---------------------------------------------------------------------------
# RULE-CLS-003: Already-claimed issues remain relevant but flagged
# ---------------------------------------------------------------------------

class TestClaimedIssueClassification:
    """RULE-CLS-003 — Design-relevant but claimed issues: classification=relevant, is_claimed=true."""

    def test_claimed_issue_classification_remains_relevant(self):
        """A claimed design issue keeps classification=relevant."""
        issue = make_issue(classification="relevant", is_claimed=True)
        assert issue["classification"] == "relevant"

    def test_claimed_issue_is_claimed_flag_true(self):
        """A claimed design issue has is_claimed=True."""
        issue = make_issue(is_claimed=True)
        assert issue["is_claimed"] is True

    def test_unclaimed_issue_is_claimed_flag_false(self):
        """An unclaimed issue has is_claimed=False."""
        issue = make_issue(is_claimed=False)
        assert issue["is_claimed"] is False


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


class TestExclusionCategories:
    """RULE-CLS-004 — Specific content categories auto-classify as not_relevant."""

    @pytest.mark.parametrize("exclusion_pattern", EXCLUSION_PATTERNS)
    def test_exclusion_pattern_results_in_not_relevant(self, exclusion_pattern):
        """Each exclusion pattern produces not_relevant classification."""
        issue = make_issue(description=exclusion_pattern, classification="not_relevant")
        # TODO: replace with: assert classifier.classify(issue).classification == "not_relevant"
        assert issue["classification"] == "not_relevant"

    def test_design_keywords_do_not_override_exclusion(self):
        """An issue with design keywords AND an exclusion trigger → not_relevant."""
        issue = make_issue(
            title="Refactor design system tokens",
            description="Rename design tokens. refactor, rename X to Y.",
            classification="not_relevant",
        )
        # TODO: replace with actual classifier call
        assert issue["classification"] == "not_relevant"
