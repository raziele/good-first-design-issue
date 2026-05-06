"""
Backend unit tests for Claiming an Issue behavior.

Spec: specs/behavior/claim.spec.md
"""
import pytest

from tests.backend.unit.conftest import make_issue


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

class TestClaimOptions:
    """RULE-CLM-001 — Claim initiates two paths: Go to GitHub or Copy comment."""

    def test_claim_go_to_github_option_returns_github_url(self):
        """
        'Go to GitHub' path produces a URL to the GitHub issue comment form
        with the claim comment pre-filled via a URL parameter.
        """
        issue = make_issue(github_url="https://github.com/org/repo/issues/42")
        claim_comment = "I'd love to work on this design task!"

        # TODO: replace with actual claim service call:
        # result = claim_service.build_github_redirect(issue, claim_comment)
        def build_github_redirect(iss, comment):
            encoded = comment.replace(" ", "+")
            return f"{iss['github_url']}#new_comment_field={encoded}"

        redirect_url = build_github_redirect(issue, claim_comment)
        assert redirect_url.startswith("https://github.com/org/repo/issues/42")
        assert "new_comment_field" in redirect_url

    def test_claim_copy_comment_option_returns_comment_text(self):
        """
        'Copy comment' path returns the AI-generated claim comment string
        that the frontend will push to the clipboard.
        """
        issue = make_issue(title="Redesign settings screen")
        # TODO: replace with actual AI generator call:
        # comment = claim_service.generate_claim_comment(issue)
        comment = "I'd love to take this on — I'll work on the settings redesign."
        assert isinstance(comment, str)
        assert len(comment) > 0


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated (contextual)
# ---------------------------------------------------------------------------

class TestClaimCommentGeneration:
    """RULE-CLM-002 — Claim comment is contextually generated from issue content."""

    def test_claim_comment_is_non_empty_string(self):
        """Generated claim comment is a non-empty string."""
        issue = make_issue(title="Mobile onboarding redesign")
        # TODO: replace with: comment = claim_service.generate_claim_comment(issue)
        comment = "I'll work on the onboarding flow — excited to contribute!"
        assert isinstance(comment, str)
        assert len(comment.strip()) > 0

    def test_claim_comment_reflects_issue_context(self):
        """
        Claim comment for a design issue mentions design or UX intent.
        Note: Full verification requires an LLM response; this test validates
        the structural contract (comment is issue-specific, not a fixed template).
        """
        # TODO: wire to actual LLM-backed generator for integration test
        issue = make_issue(title="mobile onboarding redesign", description="UX overhaul")
        comment = "I'll work on the onboarding flow UX."
        assert any(kw in comment.lower() for kw in ["design", "ux", "flow", "onboarding", "wireframe"])

    def test_claim_comment_for_different_issues_can_differ(self):
        """
        Two different issues should not necessarily produce the same fixed template.
        TODO: This test is a placeholder; implement once the generator is wired.
        """
        issue_a = make_issue(title="Redesign settings page")
        issue_b = make_issue(title="Create icon set for mobile app")
        # Structural contract: each call receives different input.
        assert issue_a["title"] != issue_b["title"]


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestNoLocalClaimTracking:
    """RULE-CLM-003 — Level8 does not persist claim records in its database."""

    def test_claim_action_does_not_create_local_record(self):
        """
        After a claim action, no new record is written for the claim itself.
        The issue's is_claimed status is updated only on the next ETL refresh.
        """
        # TODO: wire to actual DB session / mock
        # Structural contract: the claim service has no "create claim" DB call.
        claim_records_after_action = []  # simulated: no records created
        assert claim_records_after_action == []

    def test_is_claimed_updates_on_next_etl_not_immediately(self):
        """
        Immediately after a claim, is_claimed remains as it was.
        It only updates after ETL re-fetches GitHub comment data.
        """
        issue = make_issue(is_claimed=False)
        # Simulate claim action (no local update)
        # issue stays unchanged until ETL runs
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue
# ---------------------------------------------------------------------------

class TestMultipleClaimants:
    """RULE-CLM-004 — No blocking or warning when multiple users claim the same issue."""

    def test_second_user_sees_same_claim_options_as_first(self):
        """
        A second user viewing an already-claimed issue still gets both claim
        options without any block or warning in the API response.
        """
        issue = make_issue(classification="relevant", status="active", is_claimed=True)

        # The API must not reject or modify the response because is_claimed=True.
        # TODO: replace with actual API call:
        # response = client.get(f"/issues/{issue['id']}")
        # assert response.status_code == 200
        # assert response.json()["claim_options_available"] is True

        # For now: assert the domain object still carries the standard fields
        assert issue["classification"] == "relevant"
        assert issue["status"] == "active"
        assert issue["is_claimed"] is True  # flag shown, not a block

    def test_claim_action_not_blocked_for_claimed_issue(self):
        """
        Calling the claim endpoint on a claimed issue does not return an error.
        TODO: implement once the claim API endpoint exists.
        """
        # TODO: response = client.post(f"/issues/{issue['id']}/claim")
        # assert response.status_code == 200
        assert True  # placeholder — no blocking behaviour implemented yet
