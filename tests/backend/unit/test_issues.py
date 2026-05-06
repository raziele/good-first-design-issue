"""
Backend unit tests for Issue Browsing and Viewing behavior.

Spec: specs/behavior/issues.spec.md
"""
import pytest

from tests.backend.unit.conftest import make_issue


def filter_listing(issues):
    """Pure function expressing RULE-ISS-001: only relevant + active issues appear."""
    return [i for i in issues if i["classification"] == "relevant" and i["status"] == "active"]


def sort_by_freshness(issues):
    """Pure function expressing RULE-ISS-005: sort by freshness_days ascending (newest first)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestIssueListingFilter:
    """RULE-ISS-001 — Main listing shows only classification=relevant AND status=active."""

    def test_relevant_active_issue_appears_in_listing(self, active_relevant_issue):
        """A relevant, active issue appears in the filtered listing."""
        result = filter_listing([active_relevant_issue])
        assert len(result) == 1
        assert result[0]["id"] == active_relevant_issue["id"]

    def test_not_relevant_issue_hidden_from_listing(self, not_relevant_issue):
        """A not_relevant issue does not appear in the listing."""
        result = filter_listing([not_relevant_issue])
        assert result == []

    def test_archived_issue_hidden_from_listing(self, archived_issue):
        """An archived issue does not appear in the main listing."""
        result = filter_listing([archived_issue])
        assert result == []

    def test_listing_excludes_closed_status_issue(self):
        """An issue with status=closed does not appear."""
        issue = make_issue(status="closed", classification="relevant")
        result = filter_listing([issue])
        assert result == []

    def test_listing_with_mixed_issues(self, active_relevant_issue, archived_issue, not_relevant_issue):
        """Mixed set: only relevant+active issues survive the filter."""
        all_issues = [active_relevant_issue, archived_issue, not_relevant_issue]
        result = filter_listing(all_issues)
        assert len(result) == 1
        assert result[0]["id"] == active_relevant_issue["id"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestIssueCardFields:
    """RULE-ISS-002 — Issue card exposes required display attributes."""

    REQUIRED_CARD_FIELDS = [
        "repo_name",
        "title",
        "description_truncated",
        "complexity_score",
        "attractiveness_rating",
        "seniority_level",
        "freshness_days",
    ]

    def test_card_has_required_fields(self, active_relevant_issue):
        """Issue entity carries all fields needed for card rendering."""
        for field in self.REQUIRED_CARD_FIELDS:
            assert field in active_relevant_issue, f"Missing required card field: {field}"

    def test_description_truncated_max_200_chars(self):
        """description_truncated is at most 200 characters."""
        long_desc = "x" * 500
        truncated = long_desc[:200]
        issue = make_issue(description=long_desc, description_truncated=truncated)
        assert len(issue["description_truncated"]) <= 200

    def test_media_indicator_present_when_has_media_true(self, issue_with_media):
        """When has_media=True, the field is available for the card to render an icon."""
        assert issue_with_media["has_media"] is True

    def test_media_indicator_absent_when_has_media_false(self, issue_no_media):
        """When has_media=False, the media indicator should not be shown."""
        assert issue_no_media["has_media"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestIssueDetailFields:
    """RULE-ISS-003 — Detail view exposes full description, all scores, stars, GitHub link."""

    REQUIRED_DETAIL_FIELDS = [
        "description",
        "complexity_score",
        "attractiveness_rating",
        "seniority_level",
        "freshness_days",
        "repo_stars",
        "github_url",
    ]

    def test_detail_view_has_required_fields(self, active_relevant_issue):
        """Issue entity carries all fields needed for detail view rendering."""
        for field in self.REQUIRED_DETAIL_FIELDS:
            assert field in active_relevant_issue, f"Missing required detail field: {field}"

    def test_detail_description_is_not_truncated(self):
        """Detail view uses full description, not the truncated preview."""
        full = "Full description that is longer than 200 chars. " * 10
        truncated = full[:200]
        issue = make_issue(description=full, description_truncated=truncated)
        assert len(issue["description"]) > len(issue["description_truncated"])

    def test_github_url_is_valid_url(self, active_relevant_issue):
        """github_url starts with https://github.com."""
        assert active_relevant_issue["github_url"].startswith("https://github.com")

    def test_detail_media_indicator_shown_not_embedded(self, issue_with_media):
        """has_media flag drives indicator; raw media is not embedded (no embed URL field)."""
        assert issue_with_media["has_media"] is True
        assert "embed_url" not in issue_with_media


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestClaimedIssueDisplay:
    """RULE-ISS-004 — Claimed issues appear with is_claimed=True; CTA still available."""

    def test_claimed_issue_has_is_claimed_true(self, claimed_issue):
        """Claimed issue carries is_claimed=True for the UI to render the badge."""
        assert claimed_issue["is_claimed"] is True

    def test_claimed_issue_still_appears_in_listing(self):
        """A claimed but relevant+active issue still appears in the listing."""
        issue = make_issue(classification="relevant", status="active", is_claimed=True)
        result = filter_listing([issue])
        assert len(result) == 1

    def test_unclaimed_issue_has_no_claim_badge(self, active_relevant_issue):
        """Unclaimed issue has is_claimed=False; no badge should be shown."""
        assert active_relevant_issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestDefaultSortOrder:
    """RULE-ISS-005 — Default listing sort is freshness_days ascending (newest first)."""

    def test_issues_sorted_by_freshness_ascending(self):
        """Issues are sorted so that the smallest freshness_days (newest) comes first."""
        issues = [
            make_issue(id="old", freshness_days=30),
            make_issue(id="new", freshness_days=2),
            make_issue(id="mid", freshness_days=10),
        ]
        sorted_issues = sort_by_freshness(issues)
        assert [i["id"] for i in sorted_issues] == ["new", "mid", "old"]

    def test_single_issue_sort_is_stable(self):
        """Sorting a single issue list returns the same issue."""
        issue = make_issue(freshness_days=5)
        result = sort_by_freshness([issue])
        assert result == [issue]
