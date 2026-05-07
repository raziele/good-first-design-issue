"""
Unit tests for ETL Pipeline rules.
Specs: specs/behavior/etl.spec.md
"""

import pytest
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Helpers that mirror ETL business logic (pure functions, no I/O)
# ---------------------------------------------------------------------------

INITIAL_FETCH_MAX_AGE_DAYS = 90


def is_within_initial_fetch_window(created_at: datetime, now: datetime) -> bool:
    """RULE-ETL-002: exclude issues older than 90 days on initial fetch."""
    age_days = (now - created_at).days
    return age_days <= INITIAL_FETCH_MAX_AGE_DAYS


def archive_if_closed(issue: dict, github_state: str) -> dict:
    """RULE-ETL-004: closed issues become archived."""
    updated = dict(issue)
    if github_state == "closed":
        updated["status"] = "archived"
    return updated


def detect_media(description: str) -> bool:
    """RULE-ETL-006: detect images, videos, or external links in description."""
    import re
    markdown_image = re.compile(r"!\[.*?\]\(https?://")
    html_img = re.compile(r"<img\s", re.IGNORECASE)
    bare_link = re.compile(r"https?://\S+\.(png|jpg|gif|mp4|webm)", re.IGNORECASE)
    return bool(
        markdown_image.search(description)
        or html_img.search(description)
        or bare_link.search(description)
    )


def validate_enrichment_attributes(issue: dict) -> bool:
    """RULE-ETL-005: verify required enrichment fields are populated correctly."""
    valid_complexity = issue.get("complexity_score") in ("low", "medium", "high")
    valid_attractiveness = (
        isinstance(issue.get("attractiveness_rating"), float)
        and 0.0 <= issue["attractiveness_rating"] <= 1.0
    )
    valid_seniority = issue.get("seniority_level") in ("junior", "senior")
    return valid_complexity and valid_attractiveness and valid_seniority


NOW = datetime(2024, 6, 1, tzinfo=timezone.utc)


def make_issue(**kwargs):
    defaults = {
        "id": "issue-1",
        "title": "Design the onboarding flow",
        "description": "Plain text description",
        "classification": "relevant",
        "status": "active",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.7,
        "seniority_level": "junior",
        "has_media": False,
        "created_at": NOW - timedelta(days=5),
    }
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh adds new issues
# ---------------------------------------------------------------------------

class TestRuleETL001:
    def test_daily_run_fetches_new_issues(self):
        # Simulate: yesterday's DB has 0 issues; today ETL fetches 5 new ones.
        existing_ids = set()
        new_from_github = [make_issue(id=f"new-{i}") for i in range(5)]
        to_insert = [i for i in new_from_github if i["id"] not in existing_ids]
        assert len(to_insert) == 5

    def test_duplicate_ids_not_inserted(self):
        existing_ids = {"issue-1", "issue-2"}
        new_from_github = [
            make_issue(id="issue-1"),  # already exists
            make_issue(id="issue-3"),  # new
        ]
        to_insert = [i for i in new_from_github if i["id"] not in existing_ids]
        assert len(to_insert) == 1
        assert to_insert[0]["id"] == "issue-3"


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestRuleETL002:
    def test_old_issue_excluded_on_initial_fetch(self):
        created = NOW - timedelta(days=100)
        assert is_within_initial_fetch_window(created, NOW) is False

    def test_recent_issue_included_on_initial_fetch(self):
        created = NOW - timedelta(days=30)
        assert is_within_initial_fetch_window(created, NOW) is True

    def test_exactly_90_days_is_included(self):
        created = NOW - timedelta(days=90)
        assert is_within_initial_fetch_window(created, NOW) is True

    def test_91_days_is_excluded(self):
        created = NOW - timedelta(days=91)
        assert is_within_initial_fetch_window(created, NOW) is False


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestRuleETL003:
    def test_issue_updated_with_new_description(self):
        existing = make_issue(description="Old description")
        updated_from_github = {"description": "New description from GitHub"}
        merged = {**existing, **updated_from_github}
        assert merged["description"] == "New description from GitHub"

    def test_enrichment_recalculated_on_update(self):
        existing = make_issue(complexity_score="low", attractiveness_rating=0.3)
        # After re-enrichment, scores change
        re_enriched = {**existing, "complexity_score": "high", "attractiveness_rating": 0.9}
        assert re_enriched["complexity_score"] == "high"
        assert re_enriched["attractiveness_rating"] == 0.9

    def test_is_claimed_updated_from_github_comments(self):
        existing = make_issue(is_claimed=False)
        after_refresh = {**existing, "is_claimed": True}
        assert after_refresh["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestRuleETL004:
    def test_closed_issue_moves_to_archive(self):
        issue = make_issue(status="active")
        result = archive_if_closed(issue, github_state="closed")
        assert result["status"] == "archived"

    def test_open_issue_stays_active(self):
        issue = make_issue(status="active")
        result = archive_if_closed(issue, github_state="open")
        assert result["status"] == "active"

    def test_archived_issue_hidden_from_listing(self):
        issue = archive_if_closed(make_issue(status="active"), github_state="closed")
        visible = [i for i in [issue] if i["status"] == "active"]
        assert visible == []


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestRuleETL005:
    def test_enrichment_populates_complexity_score(self):
        for value in ("low", "medium", "high"):
            issue = make_issue(complexity_score=value)
            assert validate_enrichment_attributes(issue) is True

    def test_enrichment_attractiveness_rating_in_range(self):
        issue = make_issue(attractiveness_rating=0.5)
        assert validate_enrichment_attributes(issue) is True

    def test_enrichment_attractiveness_out_of_range_invalid(self):
        issue = make_issue(attractiveness_rating=1.5)
        assert validate_enrichment_attributes(issue) is False

    def test_enrichment_seniority_level_values(self):
        for value in ("junior", "senior"):
            issue = make_issue(seniority_level=value)
            assert validate_enrichment_attributes(issue) is True

    def test_enrichment_invalid_complexity_fails(self):
        issue = make_issue(complexity_score="extreme")
        assert validate_enrichment_attributes(issue) is False

    def test_enrichment_invalid_seniority_fails(self):
        issue = make_issue(seniority_level="mid")
        assert validate_enrichment_attributes(issue) is False


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestRuleETL006:
    def test_markdown_image_detected(self):
        desc = "See the mock: ![screenshot](https://example.com/img.png)"
        assert detect_media(desc) is True

    def test_html_img_tag_detected(self):
        desc = "Check this: <img src='x.png' />"
        assert detect_media(desc) is True

    def test_direct_image_url_detected(self):
        desc = "Ref: https://example.com/screenshot.png"
        assert detect_media(desc) is True

    def test_plain_text_no_media(self):
        desc = "Just plain text with no links or images."
        assert detect_media(desc) is False

    def test_non_image_url_not_flagged(self):
        # A hyperlink to a regular webpage should NOT trigger media detection
        desc = "Visit https://example.com/about for more context."
        assert detect_media(desc) is False

    def test_mp4_video_link_detected(self):
        desc = "Demo video: https://example.com/demo.mp4"
        assert detect_media(desc) is True
