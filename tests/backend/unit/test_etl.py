"""
Tests for ETL Pipeline behavior.
Spec: specs/behavior/etl.spec.md
"""
from datetime import datetime, timedelta, timezone
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_issue(**overrides):
    """Return a minimal Issue-shaped dict matching ENTITY-001."""
    base = {
        "id": "issue-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 100,
        "title": "Create wireframes for settings page",
        "description": "Please provide mockup and user flow.",
        "labels": ["design"],
        "has_media": False,
        "created_at": datetime.now(timezone.utc) - timedelta(days=5),
        "updated_at": datetime.now(timezone.utc) - timedelta(days=1),
        "freshness_days": 5,
        "classification": "relevant",
        "is_claimed": False,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
        "status": "active",
        "fetched_at": datetime.now(timezone.utc),
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestEtlAgeFilter:
    """RULE-ETL-002: 90-day cutoff on initial/reset fetch."""

    def test_etl_age_filter_old_issue_excluded_on_initial_fetch(self):
        """
        Scenario: Old issue excluded on initial fetch
        Given a "first-time fetch" operation
        And an issue was created 100 days ago
        Then the issue is not added to the database
        """
        issue = make_issue(
            created_at=datetime.now(timezone.utc) - timedelta(days=100),
            freshness_days=100,
        )
        cutoff_days = 90
        assert issue["freshness_days"] > cutoff_days, (
            "Issue older than 90 days should exceed cutoff threshold"
        )
        assert _should_exclude_by_age(issue, cutoff_days=cutoff_days), (
            "Issue created 100 days ago must be excluded on initial fetch"
        )

    def test_etl_age_filter_recent_issue_included_on_initial_fetch(self):
        """
        Scenario: Recent issue included
        Given a "first-time fetch" operation
        And an issue was created 30 days ago
        Then the issue is added to the database
        """
        issue = make_issue(
            created_at=datetime.now(timezone.utc) - timedelta(days=30),
            freshness_days=30,
        )
        cutoff_days = 90
        assert not _should_exclude_by_age(issue, cutoff_days=cutoff_days), (
            "Issue created 30 days ago must NOT be excluded on initial fetch"
        )

    def test_etl_age_filter_boundary_exactly_90_days(self):
        """Boundary: issue exactly 90 days old is not excluded (boundary inclusive)."""
        issue = make_issue(
            created_at=datetime.now(timezone.utc) - timedelta(days=90),
            freshness_days=90,
        )
        assert not _should_exclude_by_age(issue, cutoff_days=90), (
            "Issue exactly at 90-day boundary should be included"
        )


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestEtlIssueUpdate:
    """RULE-ETL-003: ETL updates existing issue fields."""

    def test_etl_issue_update_description_refreshed(self):
        """
        Scenario: Issue updated on refresh
        Given an issue exists in the database
        And the issue's description was edited on GitHub
        Then the local issue record is updated with new description
        And enrichment scores are recalculated
        """
        existing = make_issue(description="Old description", complexity_score="low")
        incoming = make_issue(description="Updated description with new mockup details")

        merged = _merge_issue(existing, incoming)

        assert merged["description"] == "Updated description with new mockup details"
        # enrichment re-run signal: fetched_at must be refreshed
        assert merged["fetched_at"] >= existing["fetched_at"]

    def test_etl_issue_update_labels_refreshed(self):
        """ETL must update labels array when GitHub labels change."""
        existing = make_issue(labels=["design"])
        incoming = make_issue(labels=["design", "good-first-issue"])

        merged = _merge_issue(existing, incoming)
        assert "good-first-issue" in merged["labels"]


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestEtlArchiving:
    """RULE-ETL-004: Closed issues move to archived status."""

    def test_etl_archiving_closed_issue_becomes_archived(self):
        """
        Scenario: Closed issue moves to archive
        Given an issue exists with status = active
        And the issue was closed on GitHub
        Then the issue's status changes to "archived"
        And the issue no longer appears in main listing
        """
        issue = make_issue(status="active")
        github_state = "closed"

        updated = _apply_github_state(issue, github_state)

        assert updated["status"] == "archived", (
            "Issue closed on GitHub must be archived locally"
        )
        assert not _is_visible_in_main_listing(updated), (
            "Archived issue must not appear in main listing"
        )

    def test_etl_archiving_open_issue_stays_active(self):
        """Open issue must remain active after ETL."""
        issue = make_issue(status="active")
        updated = _apply_github_state(issue, "open")
        assert updated["status"] == "active"


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestEtlEnrichment:
    """RULE-ETL-005: AI enrichment populates complexity, attractiveness, seniority."""

    def test_etl_enrichment_attributes_populated_for_relevant_issue(self):
        """
        Scenario: Enrichment populates attributes
        Given a newly fetched issue with classification = relevant
        When the enrichment step runs
        Then complexity_score is set to low, medium, or high
        And attractiveness_rating is set (0.0 to 1.0)
        And seniority_level is set to junior or senior
        """
        issue = make_issue(
            classification="relevant",
            complexity_score=None,
            attractiveness_rating=None,
            seniority_level=None,
        )
        enriched = _enrich_issue(issue, complexity="medium", attractiveness=0.8, seniority="junior")

        assert enriched["complexity_score"] in ("low", "medium", "high")
        assert 0.0 <= enriched["attractiveness_rating"] <= 1.0
        assert enriched["seniority_level"] in ("junior", "senior")

    def test_etl_enrichment_attractiveness_rating_range(self):
        """attractiveness_rating must never exceed 1.0 or go below 0.0."""
        for rating in [0.0, 0.5, 1.0]:
            issue = _enrich_issue(make_issue(), complexity="low", attractiveness=rating, seniority="junior")
            assert 0.0 <= issue["attractiveness_rating"] <= 1.0


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestEtlMediaDetection:
    """RULE-ETL-006: has_media derived from issue description content."""

    def test_etl_media_detection_image_markdown_sets_has_media_true(self):
        """
        Scenario: Issue with image detected
        Given an issue description containing ![screenshot](https://...)
        Then has_media = true
        """
        description = "See attached ![screenshot](https://example.com/img.png) for context."
        assert _detect_has_media(description) is True

    def test_etl_media_detection_plain_text_sets_has_media_false(self):
        """
        Scenario: Issue with no media
        Given an issue description with plain text only
        Then has_media = false
        """
        description = "Please redesign the settings page to improve usability."
        assert _detect_has_media(description) is False

    def test_etl_media_detection_external_link_sets_has_media_true(self):
        """External link in description triggers has_media = true."""
        description = "Reference: https://figma.com/file/abc123/design-spec"
        assert _detect_has_media(description) is True

    def test_etl_media_detection_empty_description(self):
        """Empty description has no media."""
        assert _detect_has_media("") is False


# ---------------------------------------------------------------------------
# Stub helpers (replace with real imports when implementation exists)
# These functions define the behavioral contract that implementation must satisfy.
# ---------------------------------------------------------------------------

def _should_exclude_by_age(issue: dict, cutoff_days: int) -> bool:
    """Return True if the issue is older than cutoff_days (should be excluded)."""
    # TODO: replace with real ETL implementation import
    return issue["freshness_days"] > cutoff_days


def _merge_issue(existing: dict, incoming: dict) -> dict:
    """Merge incoming GitHub data onto existing local record."""
    # TODO: replace with real ETL implementation import
    merged = {**existing}
    for field in ("description", "labels", "is_claimed", "updated_at", "fetched_at"):
        if field in incoming:
            merged[field] = incoming[field]
    return merged


def _apply_github_state(issue: dict, github_state: str) -> dict:
    """Apply GitHub open/closed state to local issue record."""
    # TODO: replace with real ETL implementation import
    updated = {**issue}
    if github_state == "closed":
        updated["status"] = "archived"
    return updated


def _is_visible_in_main_listing(issue: dict) -> bool:
    """Return True only if issue should appear in main listing."""
    # TODO: replace with real implementation import
    return issue["classification"] == "relevant" and issue["status"] == "active"


def _enrich_issue(issue: dict, complexity: str, attractiveness: float, seniority: str) -> dict:
    """Apply AI-enrichment attributes to an issue."""
    # TODO: replace with real ETL enrichment import
    enriched = {**issue}
    enriched["complexity_score"] = complexity
    enriched["attractiveness_rating"] = attractiveness
    enriched["seniority_level"] = seniority
    return enriched


def _detect_has_media(description: str) -> bool:
    """Return True if description contains images, videos, or external links."""
    # TODO: replace with real ETL media-detection import
    import re
    if re.search(r'!\[.*?\]\(https?://', description):
        return True
    if re.search(r'https?://', description):
        return True
    return False
