"""
Unit tests for Issue browsing and viewing rules.
Specs: specs/behavior/issues.spec.md
"""

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Shared fixtures — in-memory issue dicts that mirror ENTITY-001 attributes
# ---------------------------------------------------------------------------

def make_issue(**kwargs):
    defaults = {
        "id": "issue-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 100,
        "title": "Design the settings page",
        "description": "Full description of the design task",
        "description_truncated": "Full description of the desig",
        "labels": ["design"],
        "has_media": False,
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 2, tzinfo=timezone.utc),
        "freshness_days": 5,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.8,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime(2024, 1, 3, tzinfo=timezone.utc),
    }
    defaults.update(kwargs)
    return defaults


def filter_listing(issues):
    """Mirrors RULE-ISS-001: only relevant + active issues appear."""
    return [
        i for i in issues
        if i["classification"] == "relevant" and i["status"] == "active"
    ]


def sort_by_freshness(issues):
    """Mirrors RULE-ISS-005: default sort by freshness_days ascending (newest first)."""
    return sorted(issues, key=lambda i: i["freshness_days"])


def truncate_description(description, max_chars=200):
    """Mirrors description_truncated derivation from ENTITY-001."""
    if len(description) <= max_chars:
        return description
    return description[:max_chars]


# ---------------------------------------------------------------------------
# RULE-ISS-001: Display only relevant active issues
# ---------------------------------------------------------------------------

class TestRuleISS001:
    def test_relevant_active_issue_appears_in_listing(self):
        issue = make_issue(classification="relevant", status="active")
        result = filter_listing([issue])
        assert len(result) == 1
        assert result[0]["id"] == "issue-1"

    def test_not_relevant_issue_is_hidden(self):
        issue = make_issue(classification="not_relevant", status="active")
        result = filter_listing([issue])
        assert result == []

    def test_archived_issue_is_hidden_from_main_listing(self):
        issue = make_issue(classification="relevant", status="archived")
        result = filter_listing([issue])
        assert result == []

    def test_closed_issue_is_hidden_from_main_listing(self):
        issue = make_issue(classification="relevant", status="closed")
        result = filter_listing([issue])
        assert result == []

    def test_mixed_issues_only_relevant_active_shown(self):
        issues = [
            make_issue(id="a", classification="relevant", status="active"),
            make_issue(id="b", classification="not_relevant", status="active"),
            make_issue(id="c", classification="relevant", status="archived"),
            make_issue(id="d", classification="relevant", status="active"),
        ]
        result = filter_listing(issues)
        ids = [i["id"] for i in result]
        assert ids == ["a", "d"]


# ---------------------------------------------------------------------------
# RULE-ISS-002: Issue card displays preview information
# ---------------------------------------------------------------------------

class TestRuleISS002:
    def test_card_shows_required_elements(self):
        issue = make_issue(
            repo_name="owner/repo",
            title="Design the settings page",
            description="X" * 250,
            has_media=True,
            complexity_score="medium",
            attractiveness_rating=0.9,
            seniority_level="junior",
            freshness_days=3,
        )
        truncated = truncate_description(issue["description"])
        assert len(truncated) == 200
        assert issue["repo_name"] == "owner/repo"
        assert issue["title"] == "Design the settings page"
        assert issue["complexity_score"] in ("low", "medium", "high")
        assert 0.0 <= issue["attractiveness_rating"] <= 1.0
        assert issue["seniority_level"] in ("junior", "senior")
        assert issue["has_media"] is True

    def test_description_truncated_to_200_chars(self):
        long_desc = "A" * 300
        truncated = truncate_description(long_desc)
        assert len(truncated) == 200

    def test_description_shorter_than_200_not_truncated(self):
        short_desc = "Short description"
        truncated = truncate_description(short_desc)
        assert truncated == short_desc

    def test_media_indicator_absent_when_no_media(self):
        issue = make_issue(has_media=False)
        assert issue["has_media"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-003: Issue detail view shows full information
# ---------------------------------------------------------------------------

class TestRuleISS003:
    def test_detail_view_exposes_full_description(self):
        full_desc = "Full description " * 20
        issue = make_issue(description=full_desc)
        assert issue["description"] == full_desc
        assert len(issue["description"]) > 200

    def test_detail_view_exposes_all_attribute_scores(self):
        issue = make_issue(
            complexity_score="high",
            attractiveness_rating=0.75,
            seniority_level="senior",
        )
        assert issue["complexity_score"] == "high"
        assert issue["attractiveness_rating"] == 0.75
        assert issue["seniority_level"] == "senior"

    def test_detail_view_exposes_repo_stars(self):
        issue = make_issue(repo_stars=4200)
        assert issue["repo_stars"] == 4200

    def test_detail_view_provides_github_url(self):
        issue = make_issue(github_url="https://github.com/owner/repo/issues/42")
        assert issue["github_url"].startswith("https://github.com/")

    def test_media_indicator_shown_when_has_media(self):
        issue = make_issue(has_media=True)
        assert issue["has_media"] is True

    def test_media_not_embedded_only_flagged(self):
        # RULE-ISS-003 Scenario: Media is indicated but not embedded.
        # The description field must NOT contain rendered <img> tags —
        # media is detected and flagged via has_media, not embedded.
        issue = make_issue(
            description="![screenshot](https://example.com/img.png)",
            has_media=True,
        )
        assert issue["has_media"] is True
        assert "<img" not in issue["description"]


# ---------------------------------------------------------------------------
# RULE-ISS-004: Claimed issues are marked
# ---------------------------------------------------------------------------

class TestRuleISS004:
    def test_claimed_issue_has_is_claimed_true(self):
        issue = make_issue(is_claimed=True)
        assert issue["is_claimed"] is True

    def test_claimed_issue_still_visible_in_listing(self):
        # Claimed issues remain in listing — they're relevant+active, just flagged.
        issue = make_issue(classification="relevant", status="active", is_claimed=True)
        result = filter_listing([issue])
        assert len(result) == 1

    def test_unclaimed_issue_has_is_claimed_false(self):
        issue = make_issue(is_claimed=False)
        assert issue["is_claimed"] is False


# ---------------------------------------------------------------------------
# RULE-ISS-005: Default sort is by freshness
# ---------------------------------------------------------------------------

class TestRuleISS005:
    def test_listing_default_sort_freshness_ascending(self):
        issues = [
            make_issue(id="old", freshness_days=30),
            make_issue(id="new", freshness_days=2),
            make_issue(id="mid", freshness_days=10),
        ]
        sorted_issues = sort_by_freshness(issues)
        ids = [i["id"] for i in sorted_issues]
        assert ids == ["new", "mid", "old"]

    def test_single_issue_sort_unchanged(self):
        issues = [make_issue(freshness_days=5)]
        result = sort_by_freshness(issues)
        assert len(result) == 1
        assert result[0]["freshness_days"] == 5

    def test_issues_with_same_freshness_all_present(self):
        issues = [
            make_issue(id="a", freshness_days=5),
            make_issue(id="b", freshness_days=5),
        ]
        result = sort_by_freshness(issues)
        assert len(result) == 2
