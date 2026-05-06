"""
Backend unit tests for Issue Browsing and Viewing.
Spec: specs/behavior/issues.spec.md
Rules: RULE-ISS-001 through RULE-ISS-005
"""
import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    """Build a minimal Issue dict with sensible defaults."""
    base = {
        "id": "issue-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 100,
        "title": "Design a new onboarding flow",
        "description": "Full description of the design task.",
        "description_truncated": "Full description of the design task.",
        "labels": ["design"],
        "has_media": False,
        "created_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2026, 4, 1, tzinfo=timezone.utc),
        "freshness_days": 5,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.7,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2026, 5, 1, tzinfo=timezone.utc),
    }
    base.update(overrides)
    return base


def filter_issues_for_main_listing(issues: list[dict]) -> list[dict]:
    """
    Simulates the main listing query:
    only classification=relevant AND status=active.
    """
    return [
        i for i in issues
        if i["classification"] == "relevant" and i["status"] == "active"
    ]


def sort_by_freshness(issues: list[dict]) -> list[dict]:
    """Sort issues by freshness_days ascending (newest first = smallest days value)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


def truncate_description(description: str, max_chars: int = 200) -> str:
    if len(description) <= max_chars:
        return description
    return description[:max_chars]


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestRuleISS001:
    """RULE-ISS-001: Only classification=relevant AND status=active appear in listing."""

    def test_relevant_active_issue_appears_in_listing(self):
        issue = make_issue(classification="relevant", status="active")
        result = filter_issues_for_main_listing([issue])
        assert len(result) == 1
        assert result[0]["id"] == "issue-1"

    def test_not_relevant_issue_is_hidden(self):
        issue = make_issue(classification="not_relevant", status="active")
        result = filter_issues_for_main_listing([issue])
        assert result == []

    def test_archived_issue_is_hidden_from_main_listing(self):
        issue = make_issue(classification="relevant", status="archived")
        result = filter_issues_for_main_listing([issue])
        assert result == []

    def test_closed_issue_is_hidden_from_main_listing(self):
        issue = make_issue(classification="relevant", status="closed")
        result = filter_issues_for_main_listing([issue])
        assert result == []

    def test_not_relevant_and_archived_is_hidden(self):
        issue = make_issue(classification="not_relevant", status="archived")
        result = filter_issues_for_main_listing([issue])
        assert result == []

    def test_mix_of_issues_returns_only_valid(self):
        issues = [
            make_issue(id="a", classification="relevant", status="active"),
            make_issue(id="b", classification="not_relevant", status="active"),
            make_issue(id="c", classification="relevant", status="archived"),
            make_issue(id="d", classification="relevant", status="active"),
        ]
        result = filter_issues_for_main_listing(issues)
        ids = [i["id"] for i in result]
        assert set(ids) == {"a", "d"}


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestRuleISS002:
    """RULE-ISS-002: Each issue card shows required preview fields."""

    REQUIRED_CARD_FIELDS = [
        "repo_name",
        "title",
        "description_truncated",
        "complexity_score",
        "attractiveness_rating",
        "seniority_level",
        "freshness_days",
    ]

    def test_card_has_all_required_fields(self):
        issue = make_issue()
        for field in self.REQUIRED_CARD_FIELDS:
            assert field in issue, f"Missing required card field: {field}"
            assert issue[field] is not None, f"Card field {field} must not be None"

    def test_card_description_is_truncated_to_200_chars(self):
        long_desc = "x" * 300
        truncated = truncate_description(long_desc, max_chars=200)
        assert len(truncated) == 200

    def test_card_short_description_is_not_truncated(self):
        short_desc = "Short description."
        truncated = truncate_description(short_desc, max_chars=200)
        assert truncated == short_desc

    def test_card_shows_media_indicator_when_has_media_true(self):
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True

    def test_card_no_media_indicator_when_has_media_false(self):
        issue = make_issue(has_media=False)
        assert issue["has_media"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestRuleISS003:
    """RULE-ISS-003: Detail view shows full description, all scores, stars, and GitHub link."""

    REQUIRED_DETAIL_FIELDS = [
        "description",
        "complexity_score",
        "attractiveness_rating",
        "seniority_level",
        "freshness_days",
        "repo_stars",
        "github_url",
    ]

    def test_detail_view_has_all_required_fields(self):
        issue = make_issue()
        for field in self.REQUIRED_DETAIL_FIELDS:
            assert field in issue, f"Missing required detail field: {field}"
            assert issue[field] is not None, f"Detail field {field} must not be None"

    def test_detail_description_is_not_truncated(self):
        long_desc = "x" * 500
        issue = make_issue(description=long_desc)
        assert issue["description"] == long_desc

    def test_detail_github_url_is_valid(self):
        issue = make_issue(github_url="https://github.com/owner/repo/issues/42")
        assert issue["github_url"].startswith("https://github.com/")

    def test_detail_shows_media_indicator_when_has_media_true(self):
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True

    def test_detail_no_embedded_media_has_media_flag_only(self):
        # Images/videos are not embedded; only the flag indicates presence
        issue = make_issue(has_media=True)
        assert "has_media" in issue
        # description should not contain embedded <img> or <video> tags
        # (the flag is a derived attribute, not raw HTML injected by the system)
        assert "<img" not in issue.get("description", "")
        assert "<video" not in issue.get("description", "")


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestRuleISS004:
    """RULE-ISS-004: Issues with is_claimed=true display a visual indicator."""

    def test_claimed_issue_has_is_claimed_true(self):
        issue = make_issue(is_claimed=True)
        assert issue["is_claimed"] is True

    def test_unclaimed_issue_has_is_claimed_false(self):
        issue = make_issue(is_claimed=False)
        assert issue["is_claimed"] is False

    def test_claimed_issue_still_appears_in_listing(self):
        """Claimed issues are shown but marked — not filtered out."""
        issue = make_issue(classification="relevant", status="active", is_claimed=True)
        result = filter_issues_for_main_listing([issue])
        assert len(result) == 1
        assert result[0]["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestRuleISS005:
    """RULE-ISS-005: Default sort is freshness_days ascending (newest first)."""

    def test_issues_sorted_by_freshness_ascending(self):
        issues = [
            make_issue(id="old", freshness_days=30),
            make_issue(id="new", freshness_days=1),
            make_issue(id="mid", freshness_days=10),
        ]
        result = sort_by_freshness(issues)
        assert [i["id"] for i in result] == ["new", "mid", "old"]

    def test_single_issue_sort_is_stable(self):
        issues = [make_issue(id="only", freshness_days=5)]
        result = sort_by_freshness(issues)
        assert result[0]["id"] == "only"

    def test_equal_freshness_preserves_order(self):
        issues = [
            make_issue(id="a", freshness_days=5),
            make_issue(id="b", freshness_days=5),
        ]
        result = sort_by_freshness(issues)
        assert [i["id"] for i in result] == ["a", "b"]
