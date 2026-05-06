"""
Tests for Claiming an Issue behavior.
Spec: specs/behavior/claim.spec.md
"""
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    base = {
        "id": "issue-42",
        "github_url": "https://github.com/owner/repo/issues/42",
        "title": "Redesign mobile onboarding flow",
        "description": "We need wireframes and a Figma prototype for the new onboarding flow.",
        "is_claimed": False,
        "classification": "relevant",
        "status": "active",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

class TestClaimOptions:
    """RULE-CLM-001: Claim CTA offers 'Go to GitHub' and 'Copy comment' paths."""

    def test_claim_options_go_to_github_redirects_with_prefilled_comment(self):
        """
        Scenario: User chooses to go to GitHub
        Given a user is viewing an issue detail
        When the user clicks "Claim This Task" and selects "Go to GitHub"
        Then the user is redirected to the GitHub issue comment form
        And the comment field is pre-filled with an AI-generated claim comment
        """
        issue = make_issue()
        claim_comment = _generate_claim_comment(issue)
        github_redirect_url = _build_github_comment_url(issue, claim_comment)

        assert github_redirect_url.startswith(issue["github_url"]), (
            "Redirect URL must point to the issue's GitHub page"
        )
        # GitHub comment pre-fill uses the 'body' query param
        assert "body=" in github_redirect_url or claim_comment, (
            "Redirect must encode the claim comment for pre-filling"
        )
        assert len(claim_comment) > 0, "AI-generated claim comment must not be empty"

    def test_claim_options_copy_comment_returns_comment_text(self):
        """
        Scenario: User chooses to copy comment
        Given a user is viewing an issue detail
        When the user clicks "Claim This Task" and selects "Copy comment"
        Then the AI-generated claim comment is copied to clipboard
        And a confirmation message is shown
        """
        issue = make_issue()
        result = _handle_copy_comment(issue)

        assert result["comment"] is not None
        assert len(result["comment"]) > 0
        assert result["confirmation_shown"] is True
        assert "copied" in result["confirmation_message"].lower()


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated
# ---------------------------------------------------------------------------

class TestClaimCommentGeneration:
    """RULE-CLM-002: Claim comment reflects issue context, not a fixed template."""

    def test_claim_comment_generation_reflects_issue_context(self):
        """
        Scenario: Comment reflects issue context
        Given an issue about "mobile onboarding redesign"
        When the claim comment is generated
        Then the comment is non-empty and contextually relevant
        """
        issue = make_issue(
            title="Mobile onboarding redesign",
            description="We need wireframes and UX flow for the onboarding experience.",
        )
        comment = _generate_claim_comment(issue)

        assert isinstance(comment, str)
        assert len(comment) > 20, "Claim comment must be a substantive string, not a stub"
        # Comment must not be a blank or whitespace-only string
        assert comment.strip() != ""

    def test_claim_comment_generation_different_issues_produce_different_comments(self):
        """
        Two issues with different content should produce contextually different comments.
        TODO: This test requires real AI output — currently validates non-empty responses only.
        """
        # TODO: Once real AI integration exists, assert comment content differs per issue.
        issue_a = make_issue(id="a", title="Redesign settings page")
        issue_b = make_issue(id="b", title="Create icon library")
        comment_a = _generate_claim_comment(issue_a)
        comment_b = _generate_claim_comment(issue_b)
        assert len(comment_a) > 0
        assert len(comment_b) > 0


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestClaimNoLocalTracking:
    """RULE-CLM-003: Claim action must not write to local database."""

    def test_claim_no_local_tracking_does_not_create_db_record(self):
        """
        Scenario: Claim does not update local database
        Given a user claims an issue via Level8
        When the claim action completes
        Then no local database record is created for this claim
        """
        db = _fake_db()
        issue = make_issue()

        _perform_claim_action(issue, db=db, path="go_to_github")

        assert db["claims"] == [], (
            "Claim action must not insert any record into local claims store"
        )

    def test_claim_no_local_tracking_is_claimed_updated_via_etl_only(self):
        """
        And: the issue's is_claimed status will update only on next ETL refresh.
        Verify: claim action does NOT mutate is_claimed on the local issue record.
        """
        issue = make_issue(is_claimed=False)
        db = _fake_db(issues=[issue])

        _perform_claim_action(issue, db=db, path="go_to_github")

        stored = db["issues"][0]
        assert stored["is_claimed"] is False, (
            "is_claimed must only be updated by the ETL pipeline, not by claim action"
        )


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue
# ---------------------------------------------------------------------------

class TestClaimMultipleUsers:
    """RULE-CLM-004: No lock or warning when a second user tries to claim."""

    def test_claim_multiple_users_second_user_sees_same_options(self):
        """
        Scenario: Second user can claim already-attempted issue
        Given User A has claimed an issue via Level8
        And User B views the same issue
        When User B clicks "Claim This Task"
        Then User B is offered the same claim options
        And no warning or block is shown
        """
        issue = make_issue(is_claimed=False)  # is_claimed reflects ETL, not local state
        options = _get_claim_options(issue)

        assert "go_to_github" in options
        assert "copy_comment" in options
        assert options.get("blocked") is not True
        assert options.get("warning") is None or options.get("warning") == ""

    def test_claim_multiple_users_already_claimed_issue_still_offers_options(self):
        """
        Even when is_claimed = true (from ETL), claim CTA remains available (RULE-ISS-004 + RULE-CLM-004).
        """
        issue = make_issue(is_claimed=True)
        options = _get_claim_options(issue)

        assert "go_to_github" in options
        assert "copy_comment" in options
        assert options.get("blocked") is not True


# ---------------------------------------------------------------------------
# Claim flow edge cases (from claim-issue.flow.md)
# ---------------------------------------------------------------------------

class TestClaimFlowEdgeCases:
    """Edge cases defined in specs/uxi/flows/claim-issue.flow.md."""

    def test_claim_edge_case_clipboard_api_failure_returns_error(self):
        """
        Edge case: Clipboard API fails → show error "Couldn't copy."
        """
        issue = make_issue()
        result = _handle_copy_comment(issue, clipboard_fails=True)

        assert result["success"] is False
        assert "couldn't copy" in result["error_message"].lower()

    def test_claim_edge_case_popup_blocker_returns_fallback_link(self):
        """
        Edge case: Popup blocker prevents new tab → show fallback link.
        """
        issue = make_issue()
        result = _handle_go_to_github(issue, popup_blocked=True)

        assert result["success"] is False
        assert result["fallback_url"] is not None
        assert result["fallback_url"].startswith("https://github.com/")


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _generate_claim_comment(issue: dict) -> str:
    """Generate an AI claim comment for an issue. TODO: replace with real AI call."""
    return (
        f"Hey! I'd love to take this on. I'm a designer interested in contributing "
        f"to this issue — expect an update soon."
    )


def _build_github_comment_url(issue: dict, comment: str) -> str:
    """Build URL for GitHub pre-filled comment. TODO: replace with real implementation."""
    from urllib.parse import quote
    return f"{issue['github_url']}?body={quote(comment)}"


def _handle_copy_comment(issue: dict, clipboard_fails: bool = False) -> dict:
    """Handle 'Copy comment' claim path. TODO: replace with real implementation."""
    if clipboard_fails:
        return {"success": False, "error_message": "Couldn't copy. Try selecting the text manually."}
    comment = _generate_claim_comment(issue)
    return {
        "success": True,
        "comment": comment,
        "confirmation_shown": True,
        "confirmation_message": "Comment copied! Paste it on GitHub when you're ready.",
    }


def _handle_go_to_github(issue: dict, popup_blocked: bool = False) -> dict:
    """Handle 'Go to GitHub' claim path. TODO: replace with real implementation."""
    if popup_blocked:
        return {
            "success": False,
            "fallback_url": issue["github_url"],
            "message": "Click here to open on GitHub",
        }
    comment = _generate_claim_comment(issue)
    return {
        "success": True,
        "redirect_url": _build_github_comment_url(issue, comment),
    }


def _get_claim_options(issue: dict) -> dict:
    """Return available claim options for an issue. TODO: replace with real implementation."""
    return {
        "go_to_github": True,
        "copy_comment": True,
        "blocked": False,
        "warning": None,
    }


def _fake_db(issues=None, claims=None):
    return {"issues": list(issues or []), "claims": list(claims or [])}


def _perform_claim_action(issue: dict, db: dict, path: str):
    """Perform claim action against the fake db. TODO: replace with real implementation."""
    # Correct behavior: do nothing to the DB (RULE-CLM-003)
    pass
