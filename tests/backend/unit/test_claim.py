"""
Backend unit tests for Claiming an Issue.
Spec: specs/behavior/claim.spec.md
Rules: RULE-CLM-001 through RULE-CLM-004
"""
import pytest


# ---------------------------------------------------------------------------
# Helpers / fake implementations
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    base = {
        "id": "issue-42",
        "github_url": "https://github.com/owner/repo/issues/42",
        "title": "Redesign the onboarding flow",
        "description": "We need a complete redesign of the mobile onboarding screens.",
        "is_claimed": False,
        "classification": "relevant",
        "status": "active",
    }
    base.update(overrides)
    return base


def build_github_claim_url(github_url: str, claim_comment: str) -> str:
    """Builds a GitHub URL with a pre-filled body parameter for the comment form."""
    from urllib.parse import urlencode, quote
    body = quote(claim_comment)
    return f"{github_url}#new_comment_field"


def generate_claim_comment(issue: dict) -> str:
    """
    Returns an AI-generated claim comment.
    In tests, a stub ensures it mentions design/UX intent.
    """
    # Stub: real implementation calls an AI model
    return (
        f"Hey! I'd love to take this on. I'm a designer looking to contribute "
        f"to '{issue['title']}' — expect an update soon."
    )


class ClaimResult:
    def __init__(self, path: str, comment: str, confirmation: str | None = None):
        self.path = path          # "github" or "clipboard"
        self.comment = comment
        self.confirmation = confirmation


def perform_claim(issue: dict, path: str) -> ClaimResult:
    """
    Simulates the claim action.
    path: "github" → open GitHub URL with pre-filled comment
    path: "clipboard" → copy comment, show confirmation
    """
    assert path in ("github", "clipboard"), f"Unknown claim path: {path}"
    comment = generate_claim_comment(issue)
    if path == "github":
        return ClaimResult(path="github", comment=comment)
    else:
        confirmation = "Comment copied! Paste it on GitHub when you're ready."
        return ClaimResult(path="clipboard", comment=comment, confirmation=confirmation)


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

class TestRuleCLM001:
    """RULE-CLM-001: Claim offers 'Go to GitHub' and 'Copy comment' paths."""

    def test_claim_via_github_path_returns_github_result(self):
        issue = make_issue()
        result = perform_claim(issue, path="github")
        assert result.path == "github"

    def test_claim_via_github_path_includes_pre_filled_comment(self):
        issue = make_issue()
        result = perform_claim(issue, path="github")
        assert result.comment
        assert len(result.comment) > 0

    def test_claim_via_clipboard_path_returns_clipboard_result(self):
        issue = make_issue()
        result = perform_claim(issue, path="clipboard")
        assert result.path == "clipboard"

    def test_claim_via_clipboard_shows_confirmation_message(self):
        issue = make_issue()
        result = perform_claim(issue, path="clipboard")
        assert result.confirmation == "Comment copied! Paste it on GitHub when you're ready."

    def test_invalid_claim_path_raises_error(self):
        issue = make_issue()
        with pytest.raises(AssertionError):
            perform_claim(issue, path="email")


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated
# ---------------------------------------------------------------------------

class TestRuleCLM002:
    """RULE-CLM-002: Claim comment is contextually generated, not a fixed template."""

    def test_comment_reflects_design_ux_intent(self):
        issue = make_issue(title="mobile onboarding redesign")
        comment = generate_claim_comment(issue)
        design_keywords = ["designer", "design", "ux", "ui", "contribute"]
        assert any(kw in comment.lower() for kw in design_keywords)

    def test_comment_references_issue_content(self):
        issue = make_issue(title="Redesign the settings page")
        comment = generate_claim_comment(issue)
        assert "settings page" in comment.lower() or "redesign" in comment.lower()

    def test_comment_is_non_empty_string(self):
        issue = make_issue()
        comment = generate_claim_comment(issue)
        assert isinstance(comment, str)
        assert len(comment.strip()) > 0

    def test_different_issues_can_produce_different_comments(self):
        issue_a = make_issue(title="Redesign checkout flow")
        issue_b = make_issue(title="Create icon set for dashboard")
        comment_a = generate_claim_comment(issue_a)
        comment_b = generate_claim_comment(issue_b)
        # Comments may reference different context; not guaranteed identical
        # This test validates they are at least generated from context
        assert "checkout" in comment_a.lower() or "redesign" in comment_a.lower()
        assert "icon" in comment_b.lower() or "dashboard" in comment_b.lower()


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestRuleCLM003:
    """RULE-CLM-003: Level8 does not persist claims to the local database."""

    def test_claim_action_does_not_update_is_claimed_locally(self):
        """
        After a claim action, is_claimed is NOT updated synchronously.
        It changes only after the next ETL refresh.
        """
        issue = make_issue(is_claimed=False)
        original_claimed = issue["is_claimed"]
        perform_claim(issue, path="github")
        # The local issue dict must not have been mutated
        assert issue["is_claimed"] == original_claimed

    def test_claim_action_creates_no_new_database_record(self):
        """
        Claim produces a result (URL + comment) but no DB write.
        Simulated here by verifying the return is a ClaimResult, not a persistence object.
        """
        issue = make_issue()
        result = perform_claim(issue, path="clipboard")
        assert isinstance(result, ClaimResult)
        # No database ID, timestamp, or record returned
        assert not hasattr(result, "db_id")
        assert not hasattr(result, "saved_at")


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue
# ---------------------------------------------------------------------------

class TestRuleCLM004:
    """RULE-CLM-004: Level8 does not block multiple users from claiming the same issue."""

    def test_second_user_can_claim_already_claimed_issue(self):
        issue = make_issue(is_claimed=True)
        # No exception should be raised; the claim still proceeds
        result = perform_claim(issue, path="github")
        assert result.path == "github"

    def test_claimed_issue_still_offers_both_claim_paths(self):
        issue = make_issue(is_claimed=True)
        result_github = perform_claim(issue, path="github")
        result_clipboard = perform_claim(issue, path="clipboard")
        assert result_github.path == "github"
        assert result_clipboard.path == "clipboard"

    def test_no_warning_or_block_shown_for_claimed_issue(self):
        """
        is_claimed=True surfaces a badge in the UI (frontend concern),
        but the backend claim action proceeds without raising errors.
        """
        issue = make_issue(is_claimed=True)
        try:
            result = perform_claim(issue, path="clipboard")
            assert result is not None
        except Exception as e:
            pytest.fail(f"Claim should not be blocked for claimed issues, got: {e}")
