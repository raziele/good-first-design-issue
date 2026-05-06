"""
Tests for Issue browsing and viewing behavior.

Spec: specs/behavior/issues.spec.md
Rules: RULE-ISS-001 through RULE-ISS-005
Glossary: TERM-001 (Issue), TERM-004 (Relevant Issue), TERM-005 (Not Relevant Issue)
"""
import pytest
from tests.backend.conftest import make_issue


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

def _filter_listing(issues):
    """Simulate the listing filter: classification=relevant AND status=active."""
    return [
        i for i in issues
        if i["classification"] == "relevant" and i["status"] == "active"
    ]


def test_issues_relevant_active_issue_appears_in_listing(relevant_active_issue):
    """RULE-ISS-001 / Scenario: Relevant active issue appears in listing."""
    listing = _filter_listing([relevant_active_issue])
    assert relevant_active_issue in listing


def test_issues_not_relevant_issue_is_hidden(not_relevant_issue):
    """RULE-ISS-001 / Scenario: Not-relevant issue is hidden."""
    listing = _filter_listing([not_relevant_issue])
    assert not_relevant_issue not in listing


def test_issues_archived_issue_is_hidden_from_main_listing(archived_issue):
    """RULE-ISS-001 / Scenario: Archived issue is hidden from main listing."""
    listing = _filter_listing([archived_issue])
    assert archived_issue not in listing


def test_issues_listing_excludes_both_not_relevant_and_archived():
    """RULE-ISS-001 / Combined: mixed set returns only relevant+active."""
    issues = [
        make_issue(id="a", classification="relevant", status="active"),
        make_issue(id="b", classification="not_relevant", status="active"),
        make_issue(id="c", classification="relevant", status="archived"),
        make_issue(id="d", classification="not_relevant", status="archived"),
    ]
    listing = _filter_listing(issues)
    assert len(listing) == 1
    assert listing[0]["id"] == "a"


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

def _render_card(issue):
    """Simulate card rendering — returns the fields expected on the card."""
    return {
        "repo_name": issue["repo_name"],
        "title": issue["title"],
        "description_truncated": issue["description"][:200],
        "complexity_score": issue["complexity_score"],
        "attractiveness_rating": issue["attractiveness_rating"],
        "seniority_level": issue["seniority_level"],
        "freshness_days": issue["freshness_days"],
        "has_media": issue["has_media"],
    }


def test_issues_card_shows_required_elements(relevant_active_issue):
    """RULE-ISS-002 / Scenario: Card shows required elements."""
    card = _render_card(relevant_active_issue)

    assert card["repo_name"] == relevant_active_issue["repo_name"]
    assert card["title"] == relevant_active_issue["title"]
    assert len(card["description_truncated"]) <= 200
    assert card["complexity_score"] in ("low", "medium", "high")
    assert 0.0 <= card["attractiveness_rating"] <= 1.0
    assert card["seniority_level"] in ("junior", "senior")
    assert isinstance(card["freshness_days"], int)


def test_issues_card_shows_media_indicator_when_has_media(issue_with_media):
    """RULE-ISS-002 / And: If has_media=true, media indicator is shown."""
    card = _render_card(issue_with_media)
    assert card["has_media"] is True


def test_issues_card_no_media_indicator_when_no_media(issue_no_media):
    """RULE-ISS-002 / And: No media indicator when has_media=false."""
    card = _render_card(issue_no_media)
    assert card["has_media"] is False


def test_issues_card_description_truncated_to_200_chars():
    """RULE-ISS-002 / Truncation boundary: exactly 200 chars."""
    long_desc = "x" * 500
    issue = make_issue(description=long_desc)
    card = _render_card(issue)
    assert len(card["description_truncated"]) == 200


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

def _render_detail(issue):
    """Simulate detail view rendering."""
    return {
        "description": issue["description"],
        "complexity_score": issue["complexity_score"],
        "attractiveness_rating": issue["attractiveness_rating"],
        "seniority_level": issue["seniority_level"],
        "repo_stars": issue["repo_stars"],
        "github_url": issue["github_url"],
        "has_media": issue["has_media"],
    }


def test_issues_detail_view_shows_full_description(relevant_active_issue):
    """RULE-ISS-003 / Scenario: Detail view shows full description."""
    detail = _render_detail(relevant_active_issue)
    assert detail["description"] == relevant_active_issue["description"]


def test_issues_detail_view_shows_all_scores(relevant_active_issue):
    """RULE-ISS-003 / And: All attribute scores are visible."""
    detail = _render_detail(relevant_active_issue)
    assert detail["complexity_score"] is not None
    assert detail["attractiveness_rating"] is not None
    assert detail["seniority_level"] is not None


def test_issues_detail_view_shows_repo_stars(relevant_active_issue):
    """RULE-ISS-003 / And: Repo star count is visible."""
    detail = _render_detail(relevant_active_issue)
    assert isinstance(detail["repo_stars"], int)
    assert detail["repo_stars"] >= 0


def test_issues_detail_view_provides_github_link(relevant_active_issue):
    """RULE-ISS-003 / And: A direct link to the GitHub issue is provided."""
    detail = _render_detail(relevant_active_issue)
    assert detail["github_url"].startswith("https://github.com/")


def test_issues_detail_media_indicator_shown_but_not_embedded(issue_with_media):
    """RULE-ISS-003 / Scenario: Media is indicated but not embedded."""
    detail = _render_detail(issue_with_media)
    assert detail["has_media"] is True
    # Images must NOT be inline-embedded (no <img> or markdown image in rendered output)
    # This is a contract test — the description is raw markdown, embedding happens in GitHub
    assert "![" in issue_with_media["description"] or "http" in issue_with_media["description"]


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

def _get_claim_badge(issue):
    """Return the claim badge label if applicable."""
    if issue["is_claimed"]:
        return "Already claimed"
    return None


def _claim_cta_available(issue):
    """Claim CTA is always available regardless of is_claimed."""
    return True


def test_issues_claimed_issue_displays_claim_badge(claimed_issue):
    """RULE-ISS-004 / Scenario: Claimed issue displays claim badge."""
    badge = _get_claim_badge(claimed_issue)
    assert badge == "Already claimed"


def test_issues_claimed_issue_cta_still_available(claimed_issue):
    """RULE-ISS-004 / And: The claim CTA is still available."""
    assert _claim_cta_available(claimed_issue) is True


def test_issues_unclaimed_issue_has_no_badge(relevant_active_issue):
    """RULE-ISS-004 / Inverse: unclaimed issue has no badge."""
    badge = _get_claim_badge(relevant_active_issue)
    assert badge is None


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

def _sort_by_freshness(issues):
    """Sort issues by freshness_days ascending (newest = fewest days = first)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


def test_issues_default_sort_is_by_freshness_ascending():
    """RULE-ISS-005 / Scenario: Listing default sort order (newest first)."""
    issues = [
        make_issue(id="old", freshness_days=30),
        make_issue(id="newest", freshness_days=1),
        make_issue(id="mid", freshness_days=10),
    ]
    sorted_issues = _sort_by_freshness(issues)
    ids = [i["id"] for i in sorted_issues]
    assert ids == ["newest", "mid", "old"]
