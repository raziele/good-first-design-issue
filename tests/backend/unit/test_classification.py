"""
Tests for RULE-CLS-001 through RULE-CLS-004: Issue classification behavior.
SUT: app.classification
"""
import pytest
from app.classification import classify_issue


# ---------------------------------------------------------------------------
# RULE-CLS-001: Classification is fully automated
# ---------------------------------------------------------------------------

class TestRelevantIssueClassification:
    def test_design_issue_is_classified_as_relevant(self):
        """RULE-CLS-001: Issue with design title and Figma/mockup keywords is relevant."""
        result = classify_issue(
            title="Create wireframes for settings page",
            description="We need a mockup, user flow, and Figma file for the settings redesign.",
        )
        assert result == "relevant"

    def test_backend_issue_is_classified_as_not_relevant(self):
        """RULE-CLS-001: Issue with backend title and database keywords is not_relevant."""
        result = classify_issue(
            title="Fix API endpoint for user auth",
            description="Update the database migration and REST API handler for authentication.",
        )
        assert result == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-002: Empty descriptions are not relevant
# ---------------------------------------------------------------------------

class TestEmptyDescriptionClassification:
    def test_empty_description_is_not_relevant(self):
        """RULE-CLS-002: Issue with empty description field is not_relevant."""
        result = classify_issue(
            title="Some task",
            description="",
        )
        assert result == "not_relevant"

    def test_placeholder_only_description_is_not_relevant(self):
        """RULE-CLS-002: Description with only section headings and no content is not_relevant."""
        placeholder = "## Description\n## TODO\n## Acceptance Criteria"
        result = classify_issue(
            title="Some task",
            description=placeholder,
        )
        assert result == "not_relevant"


# ---------------------------------------------------------------------------
# RULE-CLS-004: Classification exclusion rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("exclusion_content", [
    "We need to add test coverage and unit test for the module.",
    "Fix the api endpoint, backend, and run a database migration.",
    "Please refactor the auth module and rename X to Y.",
    "implement in code the new feature in code base for the backend.",
    "Export the sprite sheet and the UTF files and game assets.",
])
def test_exclusion_pattern_classifies_as_not_relevant(exclusion_content):
    """RULE-CLS-004: Issues matching exclusion patterns are classified as not_relevant."""
    result = classify_issue(
        title="Generic task",
        description=exclusion_content,
    )
    assert result == "not_relevant"
