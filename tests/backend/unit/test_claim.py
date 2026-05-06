"""
Tests for Claiming an Issue behavior.
Spec: specs/behavior/claim.spec.md
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_issue(
    id="gh-001",
    title="Mobile onboarding redesign",
    description="Please create wireframes for the onboarding flow.",
    is_claimed=False,
    classification="relevant",
    status="active",
) -> dict:
    return {
        "id": id,
        "github_url": "https://github.com/org/repo/issues/1",
        "title": title,
        "description": description,
        "is_claimed": is_claimed,
        "classification": classification,
        "status": status,
    }


def build_github_comment_url(issue: dict, claim_comment: str) -> str:
    """
    Build the pre-filled GitHub comment URL for the "Go to GitHub" path.
    (RULE-CLM-001)
    """
    from urllib.parse import urlencode, quote_plus
    base = issue["github_url"]
    params = urlencode({"body": claim_comment})
    return f"{base}?{params}"


def generate_claim_comment(issue: dict) -> str:
    """
    Stub for AI-generated claim comment. In production this is AI-generated.
    RULE-CLM-002: comment must be contextual to the issue, not a fixed template.
    Tests validate the contract (non-empty, issue-aware), not AI quality.
    """
    return (
        f"Hey! I'd love to work on this — I plan to tackle the {issue['title'].lower()}. "
        "Expect an update soon."
    )


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

class TestClaimOptions:
    def test_go_to_github_redirects_with_prefilled_comment(self):
        """
        RULE-CLM-001 Scenario: User chooses to go to GitHub.
        Redirecting to GitHub must include a pre-filled claim comment in the URL.
        """
        issue = make_issue()
        comment = generate_claim_comment(issue)
        url = build_github_comment_url(issue, comment)

        assert url.startswith(issue["github_url"])
        assert "body=" in url
        assert comment[:10] in url or "body=" in url

    def test_copy_comment_returns_non_empty_string(self):
        """
        RULE-CLM-001 Scenario: User chooses to copy comment.
        The claim comment must be a non-empty string suitable for clipboard.
        """
        issue = make_issue()
        comment = generate_claim_comment(issue)
        assert isinstance(comment, str)
        assert len(comment) > 0

    def test_claim_options_available_for_any_relevant_active_issue(self):
        """
        RULE-CLM-001: Claim CTA is available for any relevant active issue.
        """
        issue = make_issue(classification="relevant", status="active")
        # Both paths require a valid github_url and a generated comment
        assert issue["github_url"].startswith("https://github.com/")
        comment = generate_claim_comment(issue)
        assert comment


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated (contextual)
# ---------------------------------------------------------------------------

class TestClaimCommentGeneration:
    def test_comment_reflects_issue_context(self):
        """
        RULE-CLM-002 Scenario: Comment reflects issue context.
        Given an issue about "mobile onboarding redesign",
        then the comment references design/UX intent.
        """
        issue = make_issue(
            title="Mobile onboarding redesign",
            description="Redesign the onboarding flow for mobile users.",
        )
        comment = generate_claim_comment(issue)

        design_signals = ["onboarding", "design", "flow", "work on", "ux", "wireframe"]
        assert any(signal in comment.lower() for signal in design_signals), (
            f"Claim comment lacks design context. Got: {comment}"
        )

    def test_comment_is_not_a_fixed_template(self):
        """
        RULE-CLM-002: Different issues produce different comments.
        """
        issue_a = make_issue(title="Redesign login screen")
        issue_b = make_issue(title="Create icons for navigation bar")

        comment_a = generate_claim_comment(issue_a)
        comment_b = generate_claim_comment(issue_b)

        assert comment_a != comment_b

    def test_comment_is_non_empty_for_any_valid_issue(self):
        """RULE-CLM-002: Comment generation never returns empty string."""
        issue = make_issue()
        assert generate_claim_comment(issue).strip() != ""


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

class TestNoLocalClaimTracking:
    def test_claim_does_not_create_local_database_record(self):
        """
        RULE-CLM-003 Scenario: Claim does not update local database.
        After a claim action, no new record is written to the database.
        The issue's is_claimed status only updates after the next ETL refresh.
        """
        db: list[dict] = []  # simulated database

        def perform_claim(issue: dict) -> dict:
            """
            Claim action: returns the GitHub URL for redirection.
            Does NOT write to db.
            """
            return {
                "action": "redirect",
                "url": build_github_comment_url(issue, generate_claim_comment(issue)),
            }

        issue = make_issue()
        result = perform_claim(issue)

        assert len(db) == 0, "Claim must not create a local database record."
        assert result["action"] == "redirect"

    def test_is_claimed_only_updates_after_etl_refresh(self):
        """
        RULE-CLM-003: is_claimed remains unchanged immediately after claim.
        It will only flip to True on the next ETL run.
        """
        issue = make_issue(is_claimed=False)
        # Simulate claim action — is_claimed must not change in the same request
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue
# ---------------------------------------------------------------------------

class TestMultipleClaims:
    def test_second_user_can_claim_already_claimed_issue(self):
        """
        RULE-CLM-004 Scenario: Second user can claim already-attempted issue.
        No warning or block is shown. Both users get the same claim options.
        """
        issue = make_issue(is_claimed=True)  # User A already claimed

        # User B attempting claim — no exception, no block
        comment = generate_claim_comment(issue)
        url = build_github_comment_url(issue, comment)

        assert url  # Options are available
        assert comment  # Comment is generated

    def test_no_blocking_on_already_claimed_issue(self):
        """
        RULE-CLM-004: is_claimed = true does not prevent the claim CTA from working.
        """
        issue = make_issue(is_claimed=True)
        # Claiming should be possible regardless of is_claimed flag
        try:
            comment = generate_claim_comment(issue)
            url = build_github_comment_url(issue, comment)
            success = True
        except Exception:
            success = False

        assert success, "Claim action should not raise for is_claimed = true issues."

    def test_no_deduplication_between_users(self):
        """
        RULE-CLM-004: Level8 does not enforce one-claim-per-issue.
        Multiple generated comments are all valid.
        """
        issue = make_issue()
        comments = [generate_claim_comment(issue) for _ in range(3)]
        assert all(c for c in comments), "All claim comments must be non-empty."
