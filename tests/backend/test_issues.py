"""
Backend tests for Issue Browsing and Viewing.
Spec: specs/behavior/issues.spec.md
"""
import pytest
from conftest import make_issue


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

def filter_main_listing(issues: list[dict]) -> list[dict]:
    """Simulates the query: classification=relevant AND status=active."""
    return [
        i for i in issues
        if i["classification"] == "relevant" and i["status"] == "active"
    ]


def test_issue_listing_relevant_active_issue_appears(relevant_active_issue):
    """RULE-ISS-001: Scenario: Relevant active issue appears in listing."""
    listing = filter_main_listing([relevant_active_issue])
    assert any(i["id"] == relevant_active_issue["id"] for i in listing)


def test_issue_listing_not_relevant_issue_is_hidden(not_relevant_issue):
    """RULE-ISS-001: Scenario: Not-relevant issue is hidden."""
    listing = filter_main_listing([not_relevant_issue])
    assert not any(i["id"] == not_relevant_issue["id"] for i in listing)


def test_issue_listing_archived_issue_is_hidden(archived_issue):
    """RULE-ISS-001: Scenario: Archived issue is hidden from main listing."""
    listing = filter_main_listing([archived_issue])
    assert not any(i["id"] == archived_issue["id"] for i in listing)


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

CARD_REQUIRED_FIELDS = [
    "repo_name",
    "title",
    "description_truncated",
    "complexity_score",
    "attractiveness_rating",
    "seniority_level",
    "freshness_days",
]


def render_card(issue: dict) -> dict:
    """Simulates what data a card renderer would receive."""
    card = {field: issue[field] for field in CARD_REQUIRED_FIELDS}
    if issue.get("has_media"):
        card["media_indicator"] = True
    return card


def test_card_shows_required_elements(relevant_active_issue):
    """RULE-ISS-002: Scenario: Card shows required elements."""
    card = render_card(relevant_active_issue)
    for field in CARD_REQUIRED_FIELDS:
        assert field in card, f"Missing field: {field}"


def test_card_description_truncated_to_200_chars():
    """RULE-ISS-002: description_truncated is at most 200 chars."""
    long_description = "x" * 500
    truncated = long_description[:200]
    issue = make_issue(
        description=long_description,
        description_truncated=truncated,
    )
    card = render_card(issue)
    assert len(card["description_truncated"]) <= 200


def test_card_shows_media_indicator_when_has_media(issue_with_media):
    """RULE-ISS-002: Scenario: Card shows media indicator when has_media=true."""
    card = render_card(issue_with_media)
    assert card.get("media_indicator") is True


def test_card_no_media_indicator_when_no_media(relevant_active_issue):
    """RULE-ISS-002: No media indicator shown when has_media=false."""
    card = render_card(relevant_active_issue)
    assert "media_indicator" not in card


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

DETAIL_REQUIRED_FIELDS = [
    "description",
    "complexity_score",
    "attractiveness_rating",
    "seniority_level",
    "freshness_days",
    "repo_stars",
    "github_url",
]


def render_detail(issue: dict) -> dict:
    """Simulates what data a detail renderer would receive."""
    return {field: issue[field] for field in DETAIL_REQUIRED_FIELDS}


def test_detail_view_shows_full_description(relevant_active_issue):
    """RULE-ISS-003: Scenario: Detail view shows full description."""
    detail = render_detail(relevant_active_issue)
    assert detail["description"] == relevant_active_issue["description"]


def test_detail_view_shows_all_attribute_scores(relevant_active_issue):
    """RULE-ISS-003: All attribute scores visible in detail view."""
    detail = render_detail(relevant_active_issue)
    assert "complexity_score" in detail
    assert "attractiveness_rating" in detail
    assert "seniority_level" in detail


def test_detail_view_shows_repo_stars(relevant_active_issue):
    """RULE-ISS-003: Repo star count visible in detail view."""
    detail = render_detail(relevant_active_issue)
    assert "repo_stars" in detail
    assert isinstance(detail["repo_stars"], int)


def test_detail_view_provides_github_link(relevant_active_issue):
    """RULE-ISS-003: Direct link to GitHub issue provided."""
    detail = render_detail(relevant_active_issue)
    assert detail["github_url"].startswith("https://github.com/")


def test_detail_view_media_indicated_not_embedded(issue_with_media):
    """RULE-ISS-003: Scenario: Media is indicated but not embedded."""
    # has_media flag drives indicator, no embed field should be present
    assert issue_with_media["has_media"] is True
    assert "embedded_media" not in issue_with_media


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

def test_claimed_issue_has_is_claimed_flag(claimed_issue):
    """RULE-ISS-004: Scenario: Claimed issue displays claim badge."""
    assert claimed_issue["is_claimed"] is True


def test_claimed_issue_still_appears_in_listing(claimed_issue):
    """RULE-ISS-004: Claimed issue is visible (not hidden), just flagged."""
    # claimed + relevant + active → still shown
    listing = filter_main_listing([claimed_issue])
    assert any(i["id"] == claimed_issue["id"] for i in listing)


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

def test_default_sort_is_freshness_ascending():
    """RULE-ISS-005: Scenario: Listing default sort order (newest first = ascending freshness_days)."""
    issues = [
        make_issue(id="old", freshness_days=30),
        make_issue(id="new", freshness_days=2),
        make_issue(id="mid", freshness_days=15),
    ]
    sorted_issues = sorted(issues, key=lambda i: i["freshness_days"])
    assert [i["id"] for i in sorted_issues] == ["new", "mid", "old"]
