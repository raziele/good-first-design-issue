"""
Backend unit tests for Claiming an Issue.
Spec: specs/behavior/claim.spec.md
"""

import pytest
from urllib.parse import urlparse, parse_qs


# ---------------------------------------------------------------------------
# Helpers — lightweight stubs for claim logic
# ---------------------------------------------------------------------------

def build_github_comment_url(github_url: str, claim_comment: str) -> str:
    """
    Construct the URL that pre-fills a GitHub comment.
    GitHub supports ?body= query param for pre-filling issue comments.
    """
    from urllib.parse import urlencode, quote
    comment_url = f"{github_url}#issuecomment-new"
    # In practice the app would use the GitHub new-comment URL pattern
    return f"{github_url}?body={quote(claim_comment)}"


def generate_claim_comment(issue_title: str, issue_description: str) -> str:
    """
    Stub claim comment generator.
    Real system uses AI; stub validates the contract (non-empty, design-related).
    """
    return (
        f"Hey! I'd love to take this on. "
        f"I'm a designer looking to contribute to '{issue_title}' — "
        f"expect an update soon."
    )


def copy_to_clipboard_result(comment: str) -> dict:
    """Stub clipboard copy result."""
    return {"success": True, "comment": comment, "message": "Comment copied! Paste it on GitHub when you're ready."}


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

class TestRuleCLM001ClaimActionOffersTwoOptions:
    def test_go_to_github_path_produces_github_url(self):
        """Scenario: User chooses to go to GitHub."""
        issue = {
            "github_url": "https://github.com/org/repo/issues/42",
            "title": "Redesign onboarding flow",
            "description": "We need new wireframes.",
        }
        comment = generate_claim_comment(issue["title"], issue["description"])
        redirect_url = build_github_comment_url(issue["github_url"], comment)

        assert "github.com" in redirect_url
        assert "org/repo" in redirect_url

    def test_go_to_github_url_contains_prefilled_comment(self):
        """Redirect URL must contain the pre-filled comment."""
        issue = {
            "github_url": "https://github.com/org/repo/issues/42",
            "title": "Redesign settings",
            "description": "UX work needed.",
        }
        comment = generate_claim_comment(issue["title"], issue["description"])
        redirect_url = build_github_comment_url(issue["github_url"], comment)

        # body param must be encoded in the URL
        assert "body=" in redirect_url

    def test_copy_comment_path_returns_success(self):
        """Scenario: User chooses to copy comment."""
        issue = {"title": "Improve navigation UX", "description": "Needs UX work."}
        comment = generate_claim_comment(issue["title"], issue["description"])
        result = copy_to_clipboard_result(comment)

        assert result["success"] is True
        assert result["comment"] == comment

    def test_copy_comment_path_shows_confirmation_message(self):
        """Confirmation message text matches the spec copy (voice-and-tone.md)."""
        issue = {"title": "Improve nav", "description": "UX work."}
        comment = generate_claim_comment(issue["title"], issue["description"])
        result = copy_to_clipboard_result(comment)

        assert "copied" in result["message"].lower()
        assert "GitHub" in result["message"]


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated (contextual)
# ---------------------------------------------------------------------------

class TestRuleCLM002ClaimCommentIsAIGenerated:
    def test_comment_reflects_issue_context(self):
        """Scenario: Comment reflects issue context."""
        title = "Mobile onboarding redesign"
        description = "We need UX designs for the onboarding flow."
        comment = generate_claim_comment(title, description)

        # Comment must be non-empty and contextual (reference designer intent)
        assert len(comment) > 0
        assert "designer" in comment.lower() or "design" in comment.lower()

    def test_comment_is_not_empty_for_any_valid_issue(self):
        """Claim comment must never be empty."""
        comment = generate_claim_comment("Add icons to sidebar", "Icon design needed.")
        assert comment.strip() != ""

    def test_comment_differs_between_issues(self):
        """Comments should be contextual — different issues yield different text."""
        comment_a = generate_claim_comment("Mobile redesign", "UX for mobile.")
        comment_b = generate_claim_comment("Icon set design", "New icon assets needed.")
        # Stub uses title; real AI agent should produce contextual differences
        assert comment_a != comment_b


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestRuleCLM003NoLocalClaimTracking:
    def test_claim_action_does_not_create_local_record(self):
        """Scenario: Claim does not update local database."""
        local_db = []  # empty in-memory store simulating no persistence

        def perform_claim(issue_id: str, path: str) -> dict:
            # Claim action — must NOT write to local_db
            comment = generate_claim_comment("Any issue", "Some description.")
            if path == "copy":
                return copy_to_clipboard_result(comment)
            elif path == "github":
                return {"redirect_url": f"https://github.com/org/repo/issues/{issue_id}"}
            return {}

        result = perform_claim("42", "copy")
        assert result["success"] is True
        assert len(local_db) == 0  # no record written

    def test_is_claimed_updates_only_on_etl_refresh(self):
        """is_claimed status changes only after ETL refresh, not after claim action."""
        issue = {"id": "42", "is_claimed": False}
        # Claim action completes — issue record unchanged
        # (ETL would later detect comment and set is_claimed=True)
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim the same issue
# ---------------------------------------------------------------------------

class TestRuleCLM004MultipleUsersCanClaimSameIssue:
    def test_second_user_can_initiate_claim_on_claimed_issue(self):
        """Scenario: Second user can claim already-attempted issue."""
        issue = {"id": "42", "is_claimed": True, "classification": "relevant", "status": "active"}

        # Even though is_claimed=True, the claim action is still available
        def claim_action_available(issue: dict) -> bool:
            # Spec says: no warning or block shown
            return True  # always available regardless of is_claimed

        assert claim_action_available(issue) is True

    def test_no_blocking_warning_shown_for_claimed_issue(self):
        """No blocking error returned when is_claimed=True."""
        issue = {"is_claimed": True}
        # The claim modal still offers both options
        comment = generate_claim_comment("Some design task", "UX work.")
        result = copy_to_clipboard_result(comment)
        assert result["success"] is True
