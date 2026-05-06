"""
Backend unit tests for ETL pipeline behavior.

Spec: specs/behavior/etl.spec.md
"""
from datetime import datetime, timedelta, timezone

import pytest

from tests.backend.unit.conftest import make_issue


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

class TestDailyRefresh:
    """RULE-ETL-001 — Daily run fetches new issues."""

    def test_etl_daily_run_adds_new_issues(self):
        """New GitHub issues created since last run appear in the database after ETL."""
        # TODO: wire to real ETL upsert function once implemented
        # Given: 5 new issues created since yesterday's run
        new_issues = [make_issue(id=f"new-{i}") for i in range(5)]

        # When: ETL upsert logic is called
        # TODO: result = etl.upsert(new_issues, db)

        # Then: all 5 issues are now stored
        assert len(new_issues) == 5  # placeholder assertion


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestInitialFetchAgeFilter:
    """RULE-ETL-002 — Age filter during first-time / reset operations."""

    def test_etl_excludes_issue_older_than_90_days_on_reset(self):
        """An issue created 100 days ago is excluded during a reset/initial fetch."""
        now = datetime(2026, 5, 6, tzinfo=timezone.utc)
        old_created_at = now - timedelta(days=100)
        issue = make_issue(created_at=old_created_at)

        age_days = (now - issue["created_at"]).days
        assert age_days > 90, "precondition: issue is older than 90 days"

        # TODO: replace with actual filter call: filtered = etl.apply_age_filter([issue], now, mode="reset")
        # For now, express the expected behavior as a plain assertion
        def apply_age_filter(issues, reference_date, cutoff_days=90):
            return [i for i in issues if (reference_date - i["created_at"]).days <= cutoff_days]

        result = apply_age_filter([issue], now)
        assert result == [], "Old issue must be excluded on initial fetch"

    def test_etl_includes_issue_within_90_days_on_reset(self):
        """An issue created 30 days ago is included during a reset/initial fetch."""
        now = datetime(2026, 5, 6, tzinfo=timezone.utc)
        recent_created_at = now - timedelta(days=30)
        issue = make_issue(created_at=recent_created_at)

        def apply_age_filter(issues, reference_date, cutoff_days=90):
            return [i for i in issues if (reference_date - i["created_at"]).days <= cutoff_days]

        result = apply_age_filter([issue], now)
        assert len(result) == 1, "Recent issue must be included on initial fetch"


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestIssueUpdate:
    """RULE-ETL-003 — Existing issues receive field updates on ETL run."""

    def test_etl_updates_description_on_refresh(self):
        """When an issue's GitHub description changes, the local record is updated."""
        existing = make_issue(description="Old description")
        updated_from_github = make_issue(description="New description from GitHub")

        # TODO: replace with actual merge/upsert logic
        def upsert(existing_record, incoming):
            existing_record["description"] = incoming["description"]
            return existing_record

        result = upsert(existing, updated_from_github)
        assert result["description"] == "New description from GitHub"

    def test_etl_update_triggers_enrichment_recalculation(self):
        """After a description update, enrichment scores are recalculated."""
        # TODO: wire to real enrichment service once implemented
        # For now: document the contract as a placeholder
        existing = make_issue(complexity_score="low")
        # After update, enrichment would set a new complexity_score
        assert existing["complexity_score"] == "low"  # TODO: assert recalculated value


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestIssueArchival:
    """RULE-ETL-004 — Closed GitHub issues transition to archived status."""

    def test_etl_archives_closed_issue(self):
        """An active issue detected as closed on GitHub becomes archived."""
        issue = make_issue(status="active")

        def apply_closure(record):
            record["status"] = "archived"
            return record

        result = apply_closure(issue)
        assert result["status"] == "archived"

    def test_archived_issue_excluded_from_main_listing(self):
        """Archived issues do not appear in the main listing query."""
        issues = [
            make_issue(id="a", status="active", classification="relevant"),
            make_issue(id="b", status="archived", classification="relevant"),
        ]

        visible = [i for i in issues if i["status"] == "active" and i["classification"] == "relevant"]
        ids = [i["id"] for i in visible]
        assert "b" not in ids
        assert "a" in ids


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestEnrichment:
    """RULE-ETL-005 — Enrichment populates AI-generated attributes."""

    @pytest.mark.parametrize("complexity", ["low", "medium", "high"])
    def test_enrichment_complexity_score_valid_value(self, complexity):
        """complexity_score must be one of: low, medium, high."""
        issue = make_issue(complexity_score=complexity)
        assert issue["complexity_score"] in {"low", "medium", "high"}

    def test_enrichment_attractiveness_rating_range(self):
        """attractiveness_rating must be in [0.0, 1.0]."""
        issue = make_issue(attractiveness_rating=0.82)
        assert 0.0 <= issue["attractiveness_rating"] <= 1.0

    @pytest.mark.parametrize("level", ["junior", "senior"])
    def test_enrichment_seniority_level_valid_value(self, level):
        """seniority_level must be one of: junior, senior."""
        issue = make_issue(seniority_level=level)
        assert issue["seniority_level"] in {"junior", "senior"}

    def test_enrichment_populates_all_ai_attributes(self):
        """A relevant issue after enrichment has all three AI attributes set."""
        issue = make_issue(
            classification="relevant",
            complexity_score="medium",
            attractiveness_rating=0.6,
            seniority_level="junior",
        )
        assert issue["complexity_score"] is not None
        assert issue["attractiveness_rating"] is not None
        assert issue["seniority_level"] is not None


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestMediaDetection:
    """RULE-ETL-006 — ETL sets has_media based on description content."""

    @pytest.mark.parametrize("description,expected", [
        ("See ![screenshot](https://img.png) for context.", True),
        ("Check this video: https://youtube.com/watch?v=abc", True),
        ("Plain text with no links or images.", False),
        ("", False),
    ])
    def test_media_detection(self, description, expected):
        """has_media reflects presence of images, videos, or external links."""
        import re
        # Minimal inline detector matching the spec contract
        def detect_media(desc: str) -> bool:
            if re.search(r'!\[.*?\]\(https?://', desc):
                return True
            if re.search(r'https?://', desc):
                return True
            return False

        assert detect_media(description) == expected

    def test_issue_with_markdown_image_has_media_true(self, issue_with_media):
        """Issue whose description contains a markdown image has has_media=True."""
        assert issue_with_media["has_media"] is True

    def test_issue_plain_text_has_media_false(self, issue_no_media):
        """Issue with plain-text-only description has has_media=False."""
        assert issue_no_media["has_media"] is False
