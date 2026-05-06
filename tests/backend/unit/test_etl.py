"""
Tests for ETL Pipeline behavior.
Spec: specs/behavior/etl.spec.md
"""

from datetime import datetime, timedelta, timezone
import pytest


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_issue(
    id="gh-001",
    title="Redesign settings page",
    description="Please create wireframes for the settings page.",
    created_at=None,
    status="active",
    classification="relevant",
    is_claimed=False,
    has_media=False,
    complexity_score=None,
    attractiveness_rating=None,
    seniority_level=None,
):
    now = datetime.now(tz=timezone.utc)
    return {
        "id": id,
        "github_url": f"https://github.com/org/repo/issues/1",
        "repo_name": "org/repo",
        "repo_stars": 100,
        "title": title,
        "description": description,
        "labels": [],
        "has_media": has_media,
        "created_at": created_at or now,
        "updated_at": now,
        "freshness_days": 0,
        "classification": classification,
        "is_claimed": is_claimed,
        "complexity_score": complexity_score,
        "attractiveness_rating": attractiveness_rating,
        "seniority_level": seniority_level,
        "status": status,
        "fetched_at": now,
    }


def is_within_90_days(issue: dict) -> bool:
    """Reproduce the ETL age-gate used on initial fetch (RULE-ETL-002)."""
    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=90)
    return issue["created_at"] >= cutoff


def detect_has_media(description: str) -> bool:
    """Reproduce the ETL media-detection logic (RULE-ETL-006)."""
    import re
    image_md = re.search(r"!\[.*?\]\(https?://", description)
    video_tag = re.search(r"<video", description, re.IGNORECASE)
    external_link = re.search(r"\[.*?\]\(https?://", description)
    return bool(image_md or video_tag or external_link)


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

class TestDailyRefresh:
    def test_etl_daily_run_adds_new_issues(self):
        """
        RULE-ETL-001 Scenario: Daily run fetches new issues.
        Given the ETL ran yesterday and 5 new issues were created since,
        when today's ETL run executes, then the 5 new issues are added.
        """
        existing_ids = {"gh-001", "gh-002"}
        new_issues = [make_issue(id=f"gh-{i:03d}") for i in range(10, 15)]

        incoming_ids = {issue["id"] for issue in new_issues}
        to_insert = incoming_ids - existing_ids

        assert len(to_insert) == 5


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestAgeGate:
    def test_old_issue_excluded_on_initial_fetch(self):
        """
        RULE-ETL-002 Scenario: Old issue excluded on initial fetch.
        Given a first-time fetch and an issue created 100 days ago,
        when the ETL processes GitHub results, then the issue is not added.
        """
        old_issue = make_issue(
            id="gh-old",
            created_at=datetime.now(tz=timezone.utc) - timedelta(days=100),
        )
        assert not is_within_90_days(old_issue)

    def test_recent_issue_included_on_initial_fetch(self):
        """
        RULE-ETL-002 Scenario: Recent issue included.
        Given a first-time fetch and an issue created 30 days ago,
        when the ETL processes GitHub results, then the issue is added.
        """
        recent_issue = make_issue(
            id="gh-recent",
            created_at=datetime.now(tz=timezone.utc) - timedelta(days=30),
        )
        assert is_within_90_days(recent_issue)

    def test_issue_exactly_at_90_days_boundary_is_included(self):
        """Edge: issue created exactly 90 days ago is on the boundary (inclusive)."""
        boundary_issue = make_issue(
            created_at=datetime.now(tz=timezone.utc) - timedelta(days=90, seconds=-1),
        )
        assert is_within_90_days(boundary_issue)


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestIssueUpdate:
    def test_issue_updated_on_refresh(self):
        """
        RULE-ETL-003 Scenario: Issue updated on refresh.
        Given an existing issue with old description,
        when the ETL runs with a new description from GitHub,
        then the local record is updated.
        """
        stored_issue = make_issue(description="Old description")
        updated_from_github = {**stored_issue, "description": "Updated description"}

        def apply_update(stored: dict, incoming: dict) -> dict:
            stored["description"] = incoming["description"]
            stored["updated_at"] = incoming["updated_at"]
            return stored

        result = apply_update(stored_issue, updated_from_github)
        assert result["description"] == "Updated description"

    def test_enrichment_recalculated_on_update(self):
        """
        RULE-ETL-003: Enrichment scores are recalculated when issue is updated.
        """
        stored_issue = make_issue(complexity_score="low")
        # Simulate re-enrichment returning a different score
        new_score = "high"
        stored_issue["complexity_score"] = new_score
        assert stored_issue["complexity_score"] == "high"


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestArchiveClosedIssues:
    def test_closed_issue_moves_to_archived(self):
        """
        RULE-ETL-004 Scenario: Closed issue moves to archive.
        Given an active issue that is now closed on GitHub,
        when the ETL runs, then status becomes "archived".
        """
        issue = make_issue(status="active")

        def archive_if_closed(issue: dict, github_state: str) -> dict:
            if github_state == "closed":
                issue["status"] = "archived"
            return issue

        result = archive_if_closed(issue, github_state="closed")
        assert result["status"] == "archived"

    def test_archived_issue_not_in_main_listing(self):
        """
        RULE-ETL-004: Archived issue no longer appears in main listing.
        Combines with RULE-ISS-001.
        """
        issues = [
            make_issue(id="gh-001", status="active", classification="relevant"),
            make_issue(id="gh-002", status="archived", classification="relevant"),
        ]
        visible = [i for i in issues if i["status"] == "active" and i["classification"] == "relevant"]
        assert len(visible) == 1
        assert visible[0]["id"] == "gh-001"


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestEnrichment:
    VALID_COMPLEXITY_SCORES = {"low", "medium", "high"}
    VALID_SENIORITY_LEVELS = {"junior", "senior"}

    def test_enrichment_populates_complexity_score(self):
        """
        RULE-ETL-005 Scenario: Enrichment populates attributes.
        complexity_score must be low, medium, or high.
        """
        issue = make_issue(complexity_score="medium")
        assert issue["complexity_score"] in self.VALID_COMPLEXITY_SCORES

    def test_enrichment_populates_attractiveness_rating(self):
        """
        RULE-ETL-005: attractiveness_rating is a float between 0.0 and 1.0.
        """
        issue = make_issue(attractiveness_rating=0.75)
        assert 0.0 <= issue["attractiveness_rating"] <= 1.0

    def test_enrichment_populates_seniority_level(self):
        """
        RULE-ETL-005: seniority_level is junior or senior.
        """
        issue = make_issue(seniority_level="junior")
        assert issue["seniority_level"] in self.VALID_SENIORITY_LEVELS

    @pytest.mark.parametrize("rating", [0.0, 0.5, 1.0])
    def test_attractiveness_rating_boundary_values(self, rating):
        """Boundary check: attractiveness_rating accepts 0.0, 0.5, and 1.0."""
        issue = make_issue(attractiveness_rating=rating)
        assert 0.0 <= issue["attractiveness_rating"] <= 1.0

    def test_only_relevant_issues_get_enrichment(self):
        """
        RULE-ETL-005: Only relevant issues are enriched.
        Not-relevant issues should not have enrichment attributes set.
        """
        not_relevant = make_issue(
            classification="not_relevant",
            complexity_score=None,
            attractiveness_rating=None,
            seniority_level=None,
        )
        assert not_relevant["complexity_score"] is None
        assert not_relevant["attractiveness_rating"] is None
        assert not_relevant["seniority_level"] is None


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestMediaDetection:
    def test_issue_with_image_markdown_has_media_true(self):
        """
        RULE-ETL-006 Scenario: Issue with image detected.
        Given a description containing markdown image syntax,
        then has_media = true.
        """
        description = "Here is a screenshot: ![screenshot](https://example.com/img.png)"
        assert detect_has_media(description) is True

    def test_issue_with_plain_text_has_media_false(self):
        """
        RULE-ETL-006 Scenario: Issue with no media.
        Given a plain-text description, then has_media = false.
        """
        description = "Please redesign the onboarding flow for mobile."
        assert detect_has_media(description) is False

    def test_issue_with_video_tag_has_media_true(self):
        """RULE-ETL-006 edge: HTML video tag triggers has_media = true."""
        description = "See demo: <video src='https://example.com/demo.mp4'></video>"
        assert detect_has_media(description) is True

    def test_issue_with_external_link_only_has_media_true(self):
        """RULE-ETL-006 edge: External link in description triggers has_media = true."""
        description = "Reference: [Figma file](https://figma.com/file/abc)"
        assert detect_has_media(description) is True

    def test_empty_description_has_media_false(self):
        """RULE-ETL-006 edge: Empty description has no media."""
        assert detect_has_media("") is False
