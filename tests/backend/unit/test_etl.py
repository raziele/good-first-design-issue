"""
Backend unit tests for ETL Pipeline.
Spec: specs/behavior/etl.spec.md
"""

import pytest
from datetime import datetime, timezone, timedelta
import re


# ---------------------------------------------------------------------------
# Helpers — stubs that encode ETL behavioral contracts
# ---------------------------------------------------------------------------

def compute_freshness_days(created_at: datetime, now: datetime) -> int:
    return (now - created_at).days


def is_within_initial_fetch_window(created_at: datetime, now: datetime, max_days: int = 90) -> bool:
    """RULE-ETL-002: Issues older than 90 days excluded on initial fetch."""
    return compute_freshness_days(created_at, now) <= max_days


def upsert_issue(db: dict, issue: dict) -> None:
    """Simulate INSERT OR REPLACE on issue id."""
    db[issue["id"]] = issue


def detect_has_media(description: str) -> bool:
    """RULE-ETL-006: Detect media in issue description."""
    if not description:
        return False
    image_md = re.search(r'!\[.*?\]\(https?://\S+\)', description)
    video_link = re.search(r'https?://\S+\.(mp4|webm|gif)', description, re.IGNORECASE)
    external_link = re.search(r'https?://\S+', description)
    return bool(image_md or video_link or external_link)


def archive_closed_issues(db: dict, closed_ids: set) -> None:
    """RULE-ETL-004: Set status=archived for issues closed on GitHub."""
    for issue_id, issue in db.items():
        if issue_id in closed_ids:
            issue["status"] = "archived"


def is_valid_enrichment(issue: dict) -> bool:
    """RULE-ETL-005: Enrichment populates required AI attributes."""
    return (
        issue.get("complexity_score") in ("low", "medium", "high")
        and isinstance(issue.get("attractiveness_rating"), float)
        and 0.0 <= issue["attractiveness_rating"] <= 1.0
        and issue.get("seniority_level") in ("junior", "senior")
    )


NOW = datetime(2026, 5, 7, tzinfo=timezone.utc)


def make_issue(id="1", created_at=None, status="active", description="UX design needed.", **overrides):
    base = {
        "id": id,
        "title": "Design task",
        "description": description,
        "status": status,
        "classification": "relevant",
        "is_claimed": False,
        "created_at": created_at or (NOW - timedelta(days=10)),
        "updated_at": NOW,
        "has_media": False,
        "complexity_score": None,
        "attractiveness_rating": None,
        "seniority_level": None,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

class TestRuleETL001DailyAutomatedRefresh:
    def test_daily_run_adds_new_issues(self):
        """Scenario: Daily run fetches new issues."""
        db = {}
        existing_issue = make_issue(id="existing")
        upsert_issue(db, existing_issue)

        new_issues = [make_issue(id=f"new-{i}") for i in range(5)]
        for issue in new_issues:
            upsert_issue(db, issue)

        assert len(db) == 6
        for i in range(5):
            assert f"new-{i}" in db

    def test_idempotent_upsert_does_not_duplicate(self):
        """Running ETL twice on same issue doesn't duplicate it."""
        db = {}
        issue = make_issue(id="1")
        upsert_issue(db, issue)
        upsert_issue(db, issue)
        assert len(db) == 1


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestRuleETL002IssuesOlderThan90DaysExcluded:
    def test_old_issue_excluded_on_initial_fetch(self):
        """Scenario: Old issue excluded on initial fetch."""
        created_at = NOW - timedelta(days=100)
        assert not is_within_initial_fetch_window(created_at, NOW)

    def test_recent_issue_included(self):
        """Scenario: Recent issue included."""
        created_at = NOW - timedelta(days=30)
        assert is_within_initial_fetch_window(created_at, NOW)

    def test_boundary_89_days_included(self):
        """Issue at 89 days is within window."""
        created_at = NOW - timedelta(days=89)
        assert is_within_initial_fetch_window(created_at, NOW)

    def test_boundary_90_days_included(self):
        """Issue at exactly 90 days is included (boundary)."""
        created_at = NOW - timedelta(days=90)
        assert is_within_initial_fetch_window(created_at, NOW)

    def test_boundary_91_days_excluded(self):
        """Issue at 91 days is excluded."""
        created_at = NOW - timedelta(days=91)
        assert not is_within_initial_fetch_window(created_at, NOW)

    def test_filter_batch_of_issues(self):
        """Batch filter excludes all issues older than 90 days."""
        issues = [
            make_issue(id="1", created_at=NOW - timedelta(days=30)),
            make_issue(id="2", created_at=NOW - timedelta(days=100)),
            make_issue(id="3", created_at=NOW - timedelta(days=90)),
        ]
        allowed = [i for i in issues if is_within_initial_fetch_window(i["created_at"], NOW)]
        ids = {i["id"] for i in allowed}
        assert "1" in ids
        assert "3" in ids
        assert "2" not in ids


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestRuleETL003ExistingIssuesAreUpdated:
    def test_issue_description_updated_on_refresh(self):
        """Scenario: Issue updated on refresh."""
        db = {}
        original = make_issue(id="1", description="Old description")
        upsert_issue(db, original)

        updated = make_issue(id="1", description="New description from GitHub")
        upsert_issue(db, updated)

        assert db["1"]["description"] == "New description from GitHub"

    def test_enrichment_scores_recalculated_on_refresh(self):
        """Enrichment scores are updated when an issue is refreshed."""
        db = {}
        original = make_issue(id="1", complexity_score="low", attractiveness_rating=0.3, seniority_level="junior")
        upsert_issue(db, original)

        refreshed = make_issue(id="1", complexity_score="high", attractiveness_rating=0.9, seniority_level="senior")
        upsert_issue(db, refreshed)

        assert db["1"]["complexity_score"] == "high"
        assert db["1"]["attractiveness_rating"] == 0.9
        assert db["1"]["seniority_level"] == "senior"

    def test_is_claimed_updated_on_refresh(self):
        """is_claimed field is updated during ETL refresh."""
        db = {}
        issue = make_issue(id="1", is_claimed=False)
        upsert_issue(db, issue)

        refreshed = make_issue(id="1", is_claimed=True)
        upsert_issue(db, refreshed)

        assert db["1"]["is_claimed"] is True


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestRuleETL004ClosedIssuesAreArchived:
    def test_closed_issue_moves_to_archive(self):
        """Scenario: Closed issue moves to archive."""
        db = {"1": make_issue(id="1", status="active")}
        archive_closed_issues(db, closed_ids={"1"})
        assert db["1"]["status"] == "archived"

    def test_archived_issue_excluded_from_main_listing(self):
        """Scenario: The issue no longer appears in main listing after archive."""
        db = {"1": make_issue(id="1", status="archived")}
        listing = [i for i in db.values() if i["status"] == "active"]
        assert len(listing) == 0

    def test_non_closed_issue_remains_active(self):
        """Only closed issues are archived; open ones stay active."""
        db = {
            "1": make_issue(id="1", status="active"),
            "2": make_issue(id="2", status="active"),
        }
        archive_closed_issues(db, closed_ids={"2"})
        assert db["1"]["status"] == "active"
        assert db["2"]["status"] == "archived"


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestRuleETL005EnrichmentGeneratesAIAttributes:
    def test_enrichment_populates_all_required_attributes(self):
        """Scenario: Enrichment populates attributes."""
        enriched_issue = make_issue(
            id="1",
            classification="relevant",
            complexity_score="medium",
            attractiveness_rating=0.8,
            seniority_level="junior",
        )
        assert is_valid_enrichment(enriched_issue)

    @pytest.mark.parametrize("complexity", ["low", "medium", "high"])
    def test_complexity_score_valid_values(self, complexity):
        """complexity_score must be low, medium, or high."""
        issue = make_issue(complexity_score=complexity, attractiveness_rating=0.5, seniority_level="junior")
        assert is_valid_enrichment(issue)

    @pytest.mark.parametrize("seniority", ["junior", "senior"])
    def test_seniority_level_valid_values(self, seniority):
        """seniority_level must be junior or senior."""
        issue = make_issue(complexity_score="low", attractiveness_rating=0.5, seniority_level=seniority)
        assert is_valid_enrichment(issue)

    def test_attractiveness_rating_is_between_0_and_1(self):
        """attractiveness_rating must be 0.0 to 1.0."""
        for rating in [0.0, 0.5, 1.0]:
            issue = make_issue(complexity_score="low", attractiveness_rating=rating, seniority_level="junior")
            assert is_valid_enrichment(issue)

    def test_invalid_complexity_fails_validation(self):
        """Non-spec complexity_score value fails validation."""
        issue = make_issue(complexity_score="extreme", attractiveness_rating=0.5, seniority_level="junior")
        assert not is_valid_enrichment(issue)

    def test_attractiveness_out_of_range_fails_validation(self):
        """attractiveness_rating outside 0-1 fails validation."""
        issue = make_issue(complexity_score="low", attractiveness_rating=1.5, seniority_level="junior")
        assert not is_valid_enrichment(issue)


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestRuleETL006MediaDetection:
    def test_image_markdown_detected_as_has_media_true(self):
        """Scenario: Issue with image detected."""
        description = "See the screenshot below:\n![screenshot](https://example.com/img.png)"
        assert detect_has_media(description) is True

    def test_plain_text_detected_as_has_media_false(self):
        """Scenario: Issue with no media."""
        description = "This is a plain text description with no links or images."
        assert detect_has_media(description) is False

    def test_external_link_detected_as_has_media_true(self):
        """External links count as media presence."""
        description = "See the design doc at https://figma.com/file/abc"
        assert detect_has_media(description) is True

    def test_empty_description_is_has_media_false(self):
        """Empty description has no media."""
        assert detect_has_media("") is False
        assert detect_has_media(None) is False

    def test_video_link_detected_as_has_media_true(self):
        """Video file links detected as media."""
        description = "Watch the walkthrough: https://example.com/demo.mp4"
        assert detect_has_media(description) is True
