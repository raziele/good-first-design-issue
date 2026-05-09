"""
Tests for ETL Pipeline rules.
RULE-ETL-001: Daily automated refresh
RULE-ETL-002: Issues older than 90 days excluded on initial fetch
RULE-ETL-003: Existing issues are updated
RULE-ETL-004: Closed issues are archived
RULE-ETL-005: Enrichment generates AI attributes
RULE-ETL-006: Media detection
"""

import pytest
from datetime import datetime, timezone, timedelta
from app.etl import (
    filter_issues_by_age,
    detect_media,
    archive_closed_issues,
    EnrichmentResult,
    ENRICHMENT_COMPLEXITY_VALUES,
    ENRICHMENT_SENIORITY_VALUES,
)


class TestRuleETL002AgeFilter:
    """RULE-ETL-002: Issues older than 90 days excluded on initial fetch."""

    def test_issue_over_90_days_excluded_on_initial_fetch(self):
        """Issue created 100 days ago is excluded during initial/reset fetch."""
        created_at = datetime.now(timezone.utc) - timedelta(days=100)
        issues = [{"id": "old-1", "created_at": created_at, "title": "Old issue"}]
        result = filter_issues_by_age(issues, mode="reset", cutoff_days=90)
        assert len(result) == 0

    def test_issue_within_90_days_included_on_initial_fetch(self):
        """Issue created 30 days ago is included during initial/reset fetch."""
        created_at = datetime.now(timezone.utc) - timedelta(days=30)
        issues = [{"id": "recent-1", "created_at": created_at, "title": "Recent issue"}]
        result = filter_issues_by_age(issues, mode="reset", cutoff_days=90)
        assert len(result) == 1
        assert result[0]["id"] == "recent-1"

    def test_boundary_exactly_90_days_excluded(self):
        """Issue created exactly 90 days ago is excluded (strictly older than 90 days means >90)."""
        created_at = datetime.now(timezone.utc) - timedelta(days=90, seconds=1)
        issues = [{"id": "boundary-1", "created_at": created_at}]
        result = filter_issues_by_age(issues, mode="reset", cutoff_days=90)
        assert len(result) == 0


class TestRuleETL004ClosedIssuesArchived:
    """RULE-ETL-004: Closed issues are archived."""

    def test_closed_issue_status_becomes_archived(self):
        """Issue with GitHub state=closed transitions to status=archived."""
        issues = [
            {"id": "iss-1", "status": "active", "github_state": "closed"},
            {"id": "iss-2", "status": "active", "github_state": "open"},
        ]
        result = archive_closed_issues(issues)
        archived = {i["id"]: i for i in result}
        assert archived["iss-1"]["status"] == "archived"
        assert archived["iss-2"]["status"] == "active"


class TestRuleETL005Enrichment:
    """RULE-ETL-005: Enrichment generates AI attributes."""

    def test_enrichment_result_has_required_fields(self):
        """EnrichmentResult carries complexity_score, attractiveness_rating, seniority_level."""
        result = EnrichmentResult(
            complexity_score="medium",
            attractiveness_rating=0.75,
            seniority_level="junior",
        )
        assert result.complexity_score in ENRICHMENT_COMPLEXITY_VALUES
        assert 0.0 <= result.attractiveness_rating <= 1.0
        assert result.seniority_level in ENRICHMENT_SENIORITY_VALUES

    def test_complexity_values_are_valid(self):
        """Complexity values are limited to low/medium/high."""
        assert set(ENRICHMENT_COMPLEXITY_VALUES) == {"low", "medium", "high"}

    def test_seniority_values_are_valid(self):
        """Seniority values are limited to junior/senior."""
        assert set(ENRICHMENT_SENIORITY_VALUES) == {"junior", "senior"}

    @pytest.mark.parametrize(
        "rating",
        [-0.1, 1.1, 2.0],
    )
    def test_attractiveness_rating_outside_range_raises(self, rating):
        """Attractiveness rating outside 0.0–1.0 is invalid."""
        with pytest.raises((ValueError, AssertionError)):
            EnrichmentResult(
                complexity_score="low",
                attractiveness_rating=rating,
                seniority_level="junior",
            )


class TestRuleETL006MediaDetection:
    """RULE-ETL-006: Media detection."""

    def test_markdown_image_sets_has_media_true(self):
        """Description containing markdown image syntax yields has_media=True."""
        description = "Some context.\n![screenshot](https://example.com/img.png)\nMore text."
        assert detect_media(description) is True

    def test_plain_text_sets_has_media_false(self):
        """Plain text description with no images/links yields has_media=False."""
        description = "This issue needs a redesign of the onboarding screen."
        assert detect_media(description) is False

    def test_external_link_sets_has_media_true(self):
        """Description with an external https link yields has_media=True."""
        description = "See [this Figma file](https://figma.com/file/abc123) for reference."
        assert detect_media(description) is True

    def test_empty_description_sets_has_media_false(self):
        """Empty description yields has_media=False."""
        assert detect_media("") is False
