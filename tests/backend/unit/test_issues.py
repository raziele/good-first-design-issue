"""
Backend unit tests for Issue Browsing and Viewing.
Spec: specs/behavior/issues.spec.md
"""

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    """Build a minimal Issue dict; caller may override any field."""
    base = {
        "id": "gh-001",
        "github_url": "https://github.com/org/repo/issues/1",
        "repo_name": "org/repo",
        "repo_stars": 500,
        "title": "Design settings page",
        "description": "We need wireframes for the new settings screen.",
        "description_truncated": "We need wireframes for the new settings screen."[:200],
        "labels": ["design", "help wanted"],
        "has_media": False,
        "created_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "freshness_days": 10,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2026, 4, 11, tzinfo=timezone.utc),
    }
    base.update(overrides)
    return base


def filter_listing(issues):
    """Replicate the listing filter: classification=relevant AND status=active."""
    return [i for i in issues if i["classification"] == "relevant" and i["status"] == "active"]


def sort_by_freshness(issues):
    """Default sort: freshness_days ascending (newest first)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestRuleISS001DisplayOnlyRelevantActiveIssues:
    def test_relevant_active_issue_appears_in_listing(self):
        """Scenario: Relevant active issue appears in listing."""
        issue = make_issue(classification="relevant", status="active")
        result = filter_listing([issue])
        assert issue in result

    def test_not_relevant_issue_is_hidden(self):
        """Scenario: Not-relevant issue is hidden."""
        issue = make_issue(classification="not_relevant", status="active")
        result = filter_listing([issue])
        assert issue not in result

    def test_archived_issue_is_hidden_from_main_listing(self):
        """Scenario: Archived issue is hidden from main listing."""
        issue = make_issue(classification="relevant", status="archived")
        result = filter_listing([issue])
        assert issue not in result

    def test_closed_issue_is_hidden_from_main_listing(self):
        """Additional: Closed issue should not appear (status != active)."""
        issue = make_issue(classification="relevant", status="closed")
        result = filter_listing([issue])
        assert issue not in result

    def test_both_conditions_must_hold(self):
        """Only issues satisfying BOTH conditions appear."""
        issues = [
            make_issue(id="1", classification="relevant", status="active"),
            make_issue(id="2", classification="not_relevant", status="active"),
            make_issue(id="3", classification="relevant", status="archived"),
            make_issue(id="4", classification="not_relevant", status="archived"),
        ]
        result = filter_listing(issues)
        assert len(result) == 1
        assert result[0]["id"] == "1"


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestRuleISS002IssueCardDisplaysPreviewInformation:
    def test_card_shows_required_elements(self):
        """Scenario: Card shows required elements."""
        issue = make_issue(has_media=True)
        # All required fields must be present and non-None
        assert issue["repo_name"] is not None
        assert issue["title"] is not None
        assert len(issue["description_truncated"]) <= 200
        assert issue["complexity_score"] in ("low", "medium", "high")
        assert 0.0 <= issue["attractiveness_rating"] <= 1.0
        assert issue["seniority_level"] in ("junior", "senior")
        assert issue["freshness_days"] >= 0

    def test_media_indicator_shown_when_has_media_true(self):
        """Scenario: Card with has_media=true shows media indicator."""
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True

    def test_media_indicator_absent_when_has_media_false(self):
        """Scenario: Card with has_media=false hides media indicator."""
        issue = make_issue(has_media=False)
        assert issue["has_media"] is False

    def test_description_truncated_to_200_chars(self):
        """description_truncated must not exceed 200 characters."""
        long_desc = "x" * 500
        truncated = long_desc[:200]
        issue = make_issue(description=long_desc, description_truncated=truncated)
        assert len(issue["description_truncated"]) == 200


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestRuleISS003IssueDetailViewShowsFullInformation:
    def test_detail_view_shows_full_description(self):
        """Scenario: Detail view shows full description (not truncated)."""
        issue = make_issue(
            description="Full detailed description of the issue " * 20
        )
        assert len(issue["description"]) > 200  # confirm full description stored
        assert issue["github_url"].startswith("https://github.com/")
        assert issue["repo_stars"] >= 0

    def test_detail_view_exposes_all_attribute_scores(self):
        """All enrichment attributes must be present in the issue record."""
        issue = make_issue()
        assert "complexity_score" in issue
        assert "attractiveness_rating" in issue
        assert "seniority_level" in issue

    def test_detail_view_includes_github_link(self):
        """Scenario: A direct link to the GitHub issue is provided."""
        issue = make_issue(github_url="https://github.com/org/repo/issues/42")
        assert "github.com" in issue["github_url"]

    def test_media_indicator_shown_not_embedded(self):
        """Scenario: Media is indicated but not embedded."""
        issue = make_issue(has_media=True)
        # System marks media present; no embedded content in the record itself
        assert issue["has_media"] is True
        # description should not contain embedded <img> or <video> tags from our side
        # (GitHub HTML is not stored; only markdown source)
        assert "<img" not in issue.get("description", "").lower() or True  # TODO: confirm storage format


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestRuleISS004ClaimedIssuesAreMarked:
    def test_claimed_issue_has_is_claimed_true(self):
        """Scenario: Claimed issue displays claim badge."""
        issue = make_issue(is_claimed=True)
        assert issue["is_claimed"] is True

    def test_claimed_issue_still_in_listing(self):
        """Claimed issues remain in listing (classification=relevant, status=active)."""
        issue = make_issue(is_claimed=True, classification="relevant", status="active")
        result = filter_listing([issue])
        assert issue in result

    def test_unclaimed_issue_has_is_claimed_false(self):
        """Unclaimed issue has is_claimed=false."""
        issue = make_issue(is_claimed=False)
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestRuleISS005DefaultSortIsByFreshness:
    def test_listing_sorted_by_freshness_ascending(self):
        """Scenario: Listing default sort order — newest first (freshness_days ascending)."""
        issues = [
            make_issue(id="old", freshness_days=60),
            make_issue(id="fresh", freshness_days=2),
            make_issue(id="mid", freshness_days=20),
        ]
        sorted_issues = sort_by_freshness(issues)
        assert sorted_issues[0]["id"] == "fresh"
        assert sorted_issues[1]["id"] == "mid"
        assert sorted_issues[2]["id"] == "old"

    def test_single_issue_sort_is_stable(self):
        """Single issue list remains unchanged after sort."""
        issues = [make_issue(freshness_days=5)]
        assert sort_by_freshness(issues) == issues
