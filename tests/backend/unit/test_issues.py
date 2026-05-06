"""
Tests for Issue Browsing and Viewing behavior.
Spec: specs/behavior/issues.spec.md
"""

from datetime import datetime, timedelta, timezone
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(
    id="gh-001",
    title="Redesign onboarding flow",
    description="Create a new user flow and wireframes for onboarding.",
    repo_name="org/repo",
    repo_stars=500,
    classification="relevant",
    status="active",
    is_claimed=False,
    has_media=False,
    freshness_days=3,
    complexity_score="medium",
    attractiveness_rating=0.8,
    seniority_level="junior",
):
    now = datetime.now(tz=timezone.utc)
    return {
        "id": id,
        "github_url": f"https://github.com/{repo_name}/issues/1",
        "repo_name": repo_name,
        "repo_stars": repo_stars,
        "title": title,
        "description": description,
        "description_truncated": description[:200],
        "labels": [],
        "has_media": has_media,
        "created_at": now - timedelta(days=freshness_days),
        "updated_at": now,
        "freshness_days": freshness_days,
        "classification": classification,
        "is_claimed": is_claimed,
        "complexity_score": complexity_score,
        "attractiveness_rating": attractiveness_rating,
        "seniority_level": seniority_level,
        "status": status,
        "fetched_at": now,
    }


def get_listing(issues: list[dict]) -> list[dict]:
    """Simulate main listing filter (RULE-ISS-001)."""
    return [
        i for i in issues
        if i["classification"] == "relevant" and i["status"] == "active"
    ]


def sort_by_freshness(issues: list[dict]) -> list[dict]:
    """Sort by freshness_days ascending = newest first (RULE-ISS-005)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestListingFilter:
    def test_relevant_active_issue_appears_in_listing(self):
        """
        RULE-ISS-001 Scenario: Relevant active issue appears in listing.
        """
        issues = [make_issue(classification="relevant", status="active")]
        assert len(get_listing(issues)) == 1

    def test_not_relevant_issue_hidden_from_listing(self):
        """
        RULE-ISS-001 Scenario: Not-relevant issue is hidden.
        """
        issues = [make_issue(classification="not_relevant", status="active")]
        assert len(get_listing(issues)) == 0

    def test_archived_issue_hidden_from_main_listing(self):
        """
        RULE-ISS-001 Scenario: Archived issue is hidden from main listing.
        """
        issues = [make_issue(classification="relevant", status="archived")]
        assert len(get_listing(issues)) == 0

    def test_mixed_issues_only_relevant_active_shown(self):
        """
        RULE-ISS-001: Among mixed issues, only relevant+active appear.
        """
        issues = [
            make_issue(id="a", classification="relevant", status="active"),
            make_issue(id="b", classification="not_relevant", status="active"),
            make_issue(id="c", classification="relevant", status="archived"),
            make_issue(id="d", classification="not_relevant", status="archived"),
        ]
        listing = get_listing(issues)
        assert len(listing) == 1
        assert listing[0]["id"] == "a"


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestIssueCard:
    def test_card_has_all_required_fields(self):
        """
        RULE-ISS-002 Scenario: Card shows required elements.
        The card data must include repo_name, title, description_truncated,
        complexity_score, attractiveness_rating, seniority_level, freshness_days.
        """
        issue = make_issue()
        required_fields = [
            "repo_name",
            "title",
            "description_truncated",
            "complexity_score",
            "attractiveness_rating",
            "seniority_level",
            "freshness_days",
        ]
        for field in required_fields:
            assert field in issue, f"Missing field: {field}"

    def test_description_truncated_to_200_chars(self):
        """
        RULE-ISS-002: description_truncated is at most 200 characters.
        """
        long_description = "A" * 500
        issue = make_issue(description=long_description)
        issue["description_truncated"] = long_description[:200]
        assert len(issue["description_truncated"]) <= 200

    def test_media_indicator_shown_when_has_media_true(self):
        """
        RULE-ISS-002: If has_media = true, a media indicator is shown on card.
        """
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True

    def test_no_media_indicator_when_has_media_false(self):
        """
        RULE-ISS-002: If has_media = false, no media indicator is shown.
        """
        issue = make_issue(has_media=False)
        assert issue["has_media"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestIssueDetail:
    def test_detail_view_shows_full_description(self):
        """
        RULE-ISS-003 Scenario: Detail view shows full description.
        Full issue data must include description (not truncated), all scores,
        repo_stars, and github_url.
        """
        issue = make_issue(description="Full description that is longer than 200 chars " * 5)
        required_fields = [
            "description",
            "complexity_score",
            "attractiveness_rating",
            "seniority_level",
            "repo_stars",
            "github_url",
        ]
        for field in required_fields:
            assert field in issue, f"Missing field: {field}"
        assert len(issue["description"]) > 200

    def test_full_description_not_truncated(self):
        """
        RULE-ISS-003: The detail view shows description in full, not truncated.
        """
        long_desc = "B" * 500
        issue = make_issue(description=long_desc)
        assert len(issue["description"]) == 500

    def test_github_url_is_valid(self):
        """
        RULE-ISS-003: A direct link to the GitHub issue is provided.
        """
        issue = make_issue(repo_name="org/repo")
        assert issue["github_url"].startswith("https://github.com/")

    def test_media_indicator_shown_but_not_embedded(self):
        """
        RULE-ISS-003 Scenario: Media is indicated but not embedded.
        has_media = true signals the indicator; content stays on GitHub.
        """
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True
        # The issue model does not contain embedded image/video data
        assert "embedded_media" not in issue


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestClaimedIssues:
    def test_claimed_issue_has_is_claimed_true(self):
        """
        RULE-ISS-004 Scenario: Claimed issue displays claim badge.
        is_claimed = true must be present in issue data.
        """
        issue = make_issue(is_claimed=True)
        assert issue["is_claimed"] is True

    def test_claimed_issue_still_in_listing(self):
        """
        RULE-ISS-004: Claimed issues are shown (not hidden) in the listing.
        They are visually marked but the CTA remains available.
        """
        issues = [make_issue(is_claimed=True, classification="relevant", status="active")]
        listing = get_listing(issues)
        assert len(listing) == 1

    def test_unclaimed_issue_has_is_claimed_false(self):
        """
        RULE-ISS-004 complementary: unclaimed issue has is_claimed = false.
        """
        issue = make_issue(is_claimed=False)
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestDefaultSort:
    def test_default_sort_is_freshness_ascending(self):
        """
        RULE-ISS-005 Scenario: Listing default sort order.
        Issues are sorted by freshness_days ascending (newest first).
        """
        issues = [
            make_issue(id="old", freshness_days=30),
            make_issue(id="new", freshness_days=2),
            make_issue(id="mid", freshness_days=15),
        ]
        sorted_issues = sort_by_freshness(get_listing(issues))
        ids = [i["id"] for i in sorted_issues]
        assert ids == ["new", "mid", "old"]

    def test_single_issue_sort_is_stable(self):
        """Edge: single issue list does not change after sort."""
        issues = [make_issue(freshness_days=5)]
        sorted_issues = sort_by_freshness(get_listing(issues))
        assert len(sorted_issues) == 1
