"""
Tests for RULE-CLM-001 through RULE-CLM-004: Claim behavior.
SUT: app.claim
"""
import pytest
from app.claim import build_github_comment_url, does_claim_persist_locally


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options (GitHub redirect URL construction)
# ---------------------------------------------------------------------------

class TestClaimGitHubRedirect:
    def test_github_comment_url_includes_issue_url(self):
        """RULE-CLM-001: The GitHub redirect URL encodes the issue URL."""
        github_issue_url = "https://github.com/owner/repo/issues/42"
        claim_comment = "Hey! I'd love to take this on."
        url = build_github_comment_url(github_issue_url, claim_comment)
        assert "github.com/owner/repo/issues/42" in url

    def test_github_comment_url_includes_prefilled_comment(self):
        """RULE-CLM-001: The GitHub redirect URL includes the pre-filled comment body."""
        github_issue_url = "https://github.com/owner/repo/issues/42"
        claim_comment = "I am taking this on!"
        url = build_github_comment_url(github_issue_url, claim_comment)
        # Comment body should be URL-encoded in the redirect
        assert "body=" in url

    def test_github_comment_url_is_valid_url(self):
        """RULE-CLM-001: The returned GitHub redirect URL is a valid HTTPS URL."""
        github_issue_url = "https://github.com/owner/repo/issues/7"
        url = build_github_comment_url(github_issue_url, "Claiming this!")
        assert url.startswith("https://")


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestNoLocalClaimTracking:
    def test_claim_action_does_not_persist_locally(self):
        """RULE-CLM-003: Performing a claim does not create a local record."""
        issue_id = "github-issue-99"
        persisted = does_claim_persist_locally(issue_id)
        assert persisted is False


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue
# ---------------------------------------------------------------------------

class TestMultipleClaimsAllowed:
    def test_second_claim_on_claimed_issue_is_not_blocked(self):
        """RULE-CLM-004: Claim action is available even when is_claimed=True."""
        from app.claim import is_claim_blocked
        result = is_claim_blocked(is_claimed=True)
        assert result is False

    def test_claim_on_unclaimed_issue_is_not_blocked(self):
        """RULE-CLM-004: Claim action is available when is_claimed=False."""
        from app.claim import is_claim_blocked
        result = is_claim_blocked(is_claimed=False)
        assert result is False
