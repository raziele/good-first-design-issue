"""Tests for RULE-CLM-001 through RULE-CLM-004: Claiming an Issue."""
import pytest
from app.claim import build_github_comment_url, generate_claim_comment


# ---------------------------------------------------------------------------
# RULE-CLM-001: Claim action offers two options
# ---------------------------------------------------------------------------

def test_build_github_comment_url_includes_issue_url():
    """RULE-CLM-001 — GitHub redirect URL contains the issue's html_url."""
    github_issue_url = "https://github.com/owner/repo/issues/42"
    result = build_github_comment_url(github_issue_url)
    assert "github.com/owner/repo/issues/42" in result


def test_build_github_comment_url_includes_prefilled_comment(relevant_active_issue):
    """RULE-CLM-001 — GitHub redirect URL encodes a pre-filled comment body."""
    github_issue_url = relevant_active_issue["github_url"]
    result = build_github_comment_url(github_issue_url, comment="I'll take this on!")
    assert "I" in result or "%49" in result or "body=" in result


# ---------------------------------------------------------------------------
# RULE-CLM-002: Claim comment is AI-generated and context-aware
# ---------------------------------------------------------------------------

def test_generate_claim_comment_returns_non_empty(relevant_active_issue):
    """RULE-CLM-002 — claim comment generation returns a non-empty string."""
    comment = generate_claim_comment(relevant_active_issue)
    assert isinstance(comment, str)
    assert len(comment.strip()) > 0


def test_generate_claim_comment_references_design_intent():
    """RULE-CLM-002 — comment for a design issue references design/UX intent."""
    issue = {
        "id": "github_1",
        "title": "Mobile onboarding redesign",
        "description": "Redesign the entire onboarding flow with new UX patterns.",
        "classification": "relevant",
    }
    comment = generate_claim_comment(issue)
    design_terms = ["design", "ux", "ui", "onboarding", "flow", "wireframe", "work on"]
    assert any(term.lower() in comment.lower() for term in design_terms), (
        f"Expected design-related term in claim comment, got: {comment!r}"
    )


# ---------------------------------------------------------------------------
# RULE-CLM-003: No local claim tracking
# ---------------------------------------------------------------------------

def test_claim_does_not_return_database_record(relevant_active_issue):
    """RULE-CLM-003 — claim action produces no local DB mutation record."""
    from app.claim import execute_claim
    result = execute_claim(relevant_active_issue, option="copy")
    assert result.get("db_record_created") is not True


# ---------------------------------------------------------------------------
# RULE-CLM-004: Multiple users can claim same issue (no blocking)
# ---------------------------------------------------------------------------

def test_claim_options_available_even_if_already_claimed(claimed_relevant_issue):
    """RULE-CLM-004 — claim options are available even when issue is already claimed."""
    from app.claim import get_claim_options
    options = get_claim_options(claimed_relevant_issue)
    assert "go_to_github" in options
    assert "copy_comment" in options


def test_claim_options_no_blocking_warning_for_claimed_issue(claimed_relevant_issue):
    """RULE-CLM-004 — no blocking or hard warning prevents claiming a claimed issue."""
    from app.claim import get_claim_options
    options = get_claim_options(claimed_relevant_issue)
    assert options.get("blocked") is not True
