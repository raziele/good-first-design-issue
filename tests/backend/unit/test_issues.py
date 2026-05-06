"""
Tests for Issue Browsing and Viewing behavior.
Spec: specs/behavior/issues.spec.md
"""
from datetime import datetime, timedelta, timezone
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    base = {
        "id": "issue-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 250,
        "title": "Create wireframes for onboarding",
        "description": "A" * 300,  # long description to test truncation
        "description_truncated": "A" * 200,
        "labels": ["design"],
        "has_media": False,
        "created_at": datetime.now(timezone.utc) - timedelta(days=3),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
        "freshness_days": 3,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.8,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


def filter_main_listing(issues: list) -> list:
    """Apply RULE-ISS-001 filter: relevant + active only."""
    return [i for i in issues if i["classification"] == "relevant" and i["status"] == "active"]


def sort_by_freshness(issues: list) -> list:
    """RULE-ISS-005: ascending freshness_days (newest first)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestIssueListingFilter:
    """RULE-ISS-001: Only relevant + active issues appear in main listing."""

    def test_issues_listing_filter_relevant_active_issue_appears(self):
        """
        Scenario: Relevant active issue appears in listing
        Given an issue with classification "relevant" and status "active"
        Then the issue appears in the listing
        """
        issue = make_issue(classification="relevant", status="active")
        result = filter_main_listing([issue])
        assert issue in result

    def test_issues_listing_filter_not_relevant_issue_hidden(self):
        """
        Scenario: Not-relevant issue is hidden
        Given an issue with classification "not_relevant"
        Then the issue does not appear
        """
        issue = make_issue(classification="not_relevant", status="active")
        result = filter_main_listing([issue])
        assert issue not in result

    def test_issues_listing_filter_archived_issue_hidden(self):
        """
        Scenario: Archived issue is hidden from main listing
        Given an issue with status "archived"
        Then the issue does not appear
        """
        issue = make_issue(classification="relevant", status="archived")
        result = filter_main_listing([issue])
        assert issue not in result

    def test_issues_listing_filter_closed_status_hidden(self):
        """Issue with status "closed" must also not appear."""
        issue = make_issue(classification="relevant", status="closed")
        result = filter_main_listing([issue])
        assert issue not in result

    def test_issues_listing_filter_mixed_set(self):
        """Only relevant+active issues pass through from a mixed set."""
        issues = [
            make_issue(id="a", classification="relevant", status="active"),
            make_issue(id="b", classification="not_relevant", status="active"),
            make_issue(id="c", classification="relevant", status="archived"),
            make_issue(id="d", classification="relevant", status="active"),
        ]
        result = filter_main_listing(issues)
        ids = [i["id"] for i in result]
        assert ids == ["a", "d"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestIssueCardContent:
    """RULE-ISS-002: Card must include specific required fields."""

    def test_issues_card_shows_required_elements(self):
        """
        Scenario: Card shows required elements
        Given a relevant active issue with all attributes populated
        Then card displays repo name, title, truncated description (~200 chars),
        complexity score, attractiveness rating, seniority level, freshness indicator
        """
        issue = make_issue(has_media=False)
        card = _render_card(issue)

        assert card["repo_name"] == issue["repo_name"]
        assert card["title"] == issue["title"]
        assert len(card["description_truncated"]) <= 200
        assert card["complexity_score"] in ("low", "medium", "high")
        assert 0.0 <= card["attractiveness_rating"] <= 1.0
        assert card["seniority_level"] in ("junior", "senior")
        assert "freshness_days" in card

    def test_issues_card_shows_media_indicator_when_has_media(self):
        """
        Scenario: Card shows media indicator
        Given an issue with has_media = true
        Then a media indicator is shown on the card
        """
        issue = make_issue(has_media=True)
        card = _render_card(issue)
        assert card["show_media_indicator"] is True

    def test_issues_card_hides_media_indicator_when_no_media(self):
        """Card must not show media indicator when has_media = false."""
        issue = make_issue(has_media=False)
        card = _render_card(issue)
        assert card["show_media_indicator"] is False

    def test_issues_card_truncates_description_at_200_chars(self):
        """description_truncated must be at most 200 characters."""
        long_desc = "X" * 500
        issue = make_issue(description=long_desc)
        card = _render_card(issue)
        assert len(card["description_truncated"]) <= 200


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestIssueDetailView:
    """RULE-ISS-003: Detail view exposes full description and all scores."""

    def test_issues_detail_view_shows_full_description(self):
        """
        Scenario: Detail view shows full description
        Given a user clicks on an issue card
        Then full issue description is displayed (not truncated)
        And all attribute scores are visible
        And repo star count is visible
        And a direct link to the GitHub issue is provided
        """
        issue = make_issue()
        detail = _render_detail(issue)

        assert detail["description"] == issue["description"]
        assert detail["complexity_score"] is not None
        assert detail["attractiveness_rating"] is not None
        assert detail["seniority_level"] is not None
        assert detail["repo_stars"] is not None
        assert detail["github_url"].startswith("https://github.com/")

    def test_issues_detail_view_media_indicated_not_embedded(self):
        """
        Scenario: Media is indicated but not embedded
        Given an issue with has_media = true
        Then a media indicator is shown
        But images/videos are not embedded
        """
        issue = make_issue(has_media=True)
        detail = _render_detail(issue)

        assert detail["show_media_indicator"] is True
        assert detail.get("embedded_images") is None or detail.get("embedded_images") == []


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestClaimedIssueDisplay:
    """RULE-ISS-004: Claimed issues show visual indicator but remain actionable."""

    def test_issues_claimed_badge_shown_when_is_claimed_true(self):
        """
        Scenario: Claimed issue displays claim badge
        Given an issue with is_claimed = true
        Then a visual indicator shows "Already claimed"
        And the claim CTA is still available
        """
        issue = make_issue(is_claimed=True)
        rendered = _render_detail(issue)

        assert rendered["show_claimed_badge"] is True
        assert rendered["claim_cta_enabled"] is True

    def test_issues_claimed_badge_absent_when_not_claimed(self):
        """Unclaimed issue must not show the claimed badge."""
        issue = make_issue(is_claimed=False)
        rendered = _render_detail(issue)
        assert rendered["show_claimed_badge"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestIssueDefaultSort:
    """RULE-ISS-005: Issues sorted by freshness_days ascending (newest first)."""

    def test_issues_default_sort_by_freshness_ascending(self):
        """
        Scenario: Listing default sort order
        Given multiple relevant active issues with different freshness values
        Then issues are sorted by freshness_days ascending (newest first)
        """
        issues = [
            make_issue(id="old", freshness_days=30),
            make_issue(id="newest", freshness_days=1),
            make_issue(id="mid", freshness_days=10),
        ]
        sorted_issues = sort_by_freshness(issues)
        assert [i["id"] for i in sorted_issues] == ["newest", "mid", "old"]

    def test_issues_default_sort_ties_stable(self):
        """Issues with equal freshness must both appear (order stable, not dropped)."""
        issues = [
            make_issue(id="a", freshness_days=5),
            make_issue(id="b", freshness_days=5),
        ]
        sorted_issues = sort_by_freshness(issues)
        assert len(sorted_issues) == 2


# ---------------------------------------------------------------------------
# Stub helpers
# ---------------------------------------------------------------------------

def _render_card(issue: dict) -> dict:
    """Build card view dict from an issue. TODO: replace with real frontend/API import."""
    desc = issue.get("description", "")
    return {
        "repo_name": issue["repo_name"],
        "title": issue["title"],
        "description_truncated": desc[:200],
        "complexity_score": issue["complexity_score"],
        "attractiveness_rating": issue["attractiveness_rating"],
        "seniority_level": issue["seniority_level"],
        "freshness_days": issue["freshness_days"],
        "show_media_indicator": issue.get("has_media", False),
    }


def _render_detail(issue: dict) -> dict:
    """Build detail view dict from an issue. TODO: replace with real frontend/API import."""
    return {
        "description": issue["description"],
        "complexity_score": issue.get("complexity_score"),
        "attractiveness_rating": issue.get("attractiveness_rating"),
        "seniority_level": issue.get("seniority_level"),
        "repo_stars": issue.get("repo_stars"),
        "github_url": issue.get("github_url", ""),
        "show_media_indicator": issue.get("has_media", False),
        "embedded_images": [],
        "show_claimed_badge": issue.get("is_claimed", False),
        "claim_cta_enabled": True,
    }
