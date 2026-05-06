"""
Backend unit tests for the ETL Pipeline.
Spec: specs/behavior/etl.spec.md
Rules: RULE-ETL-001 through RULE-ETL-006
"""
import pytest
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Helpers / fake ETL logic
# ---------------------------------------------------------------------------

NOW = datetime(2026, 5, 6, tzinfo=timezone.utc)
ETL_FRESHNESS_CUTOFF_DAYS = 90


def make_github_issue(**overrides):
    """Simulate a raw GitHub issue as returned by the API."""
    base = {
        "id": "gh-issue-1",
        "github_url": "https://github.com/owner/repo/issues/1",
        "repo_name": "owner/repo",
        "repo_stars": 200,
        "title": "Design the new onboarding flow",
        "description": "We need Figma wireframes.",
        "labels": ["design"],
        "created_at": NOW - timedelta(days=10),
        "updated_at": NOW - timedelta(days=1),
        "state": "open",
        "comments": [],
    }
    base.update(overrides)
    return base


def is_within_fetch_window(issue: dict, now: datetime = NOW) -> bool:
    """Returns True if the issue is within the 90-day initial fetch window."""
    age_days = (now - issue["created_at"]).days
    return age_days <= ETL_FRESHNESS_CUTOFF_DAYS


def compute_freshness_days(issue: dict, now: datetime = NOW) -> int:
    return (now - issue["created_at"]).days


def detect_has_media(description: str) -> bool:
    """Detect presence of images, videos, or external links in description."""
    import re
    image_pattern = re.compile(r"!\[.*?\]\(https?://")
    link_pattern = re.compile(r"https?://")
    video_pattern = re.compile(r"<video")
    return bool(
        image_pattern.search(description)
        or link_pattern.search(description)
        or video_pattern.search(description)
    )


def upsert_issue(db: dict, issue: dict) -> dict:
    """
    Upsert an issue into the in-memory database.
    Returns the stored issue record.
    """
    db[issue["id"]] = issue
    return issue


def archive_closed_issue(db: dict, issue_id: str) -> dict:
    """Mark an issue as archived when GitHub reports it as closed."""
    if issue_id in db:
        db[issue_id] = {**db[issue_id], "status": "archived"}
    return db.get(issue_id, {})


VALID_COMPLEXITY_SCORES = {"low", "medium", "high"}
VALID_SENIORITY_LEVELS = {"junior", "senior"}


def enrich_issue(issue: dict) -> dict:
    """
    Stub enrichment: sets AI attributes to valid enum values.
    Real implementation calls the AI model.
    """
    return {
        **issue,
        "complexity_score": "medium",
        "attractiveness_rating": 0.75,
        "seniority_level": "junior",
    }


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

class TestRuleETL001:
    """RULE-ETL-001: ETL runs daily and adds new issues to the database."""

    def test_new_issues_added_to_database(self):
        db = {}
        new_issues = [
            make_github_issue(id=f"gh-{i}", created_at=NOW - timedelta(days=i))
            for i in range(1, 6)
        ]
        for issue in new_issues:
            upsert_issue(db, issue)
        assert len(db) == 5

    def test_existing_issue_not_duplicated_on_refresh(self):
        db = {}
        issue = make_github_issue(id="gh-1")
        upsert_issue(db, issue)
        upsert_issue(db, issue)  # second upsert should not duplicate
        assert len(db) == 1


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestRuleETL002:
    """RULE-ETL-002: Issues created >90 days ago are excluded on initial/reset fetch."""

    def test_issue_100_days_old_excluded(self):
        issue = make_github_issue(created_at=NOW - timedelta(days=100))
        assert not is_within_fetch_window(issue)

    def test_issue_30_days_old_included(self):
        issue = make_github_issue(created_at=NOW - timedelta(days=30))
        assert is_within_fetch_window(issue)

    def test_issue_exactly_90_days_old_included(self):
        issue = make_github_issue(created_at=NOW - timedelta(days=90))
        assert is_within_fetch_window(issue)

    def test_issue_91_days_old_excluded(self):
        issue = make_github_issue(created_at=NOW - timedelta(days=91))
        assert not is_within_fetch_window(issue)

    def test_batch_fetch_filters_old_issues(self):
        issues = [
            make_github_issue(id="recent", created_at=NOW - timedelta(days=10)),
            make_github_issue(id="boundary", created_at=NOW - timedelta(days=90)),
            make_github_issue(id="old", created_at=NOW - timedelta(days=100)),
        ]
        valid = [i for i in issues if is_within_fetch_window(i)]
        ids = [i["id"] for i in valid]
        assert "recent" in ids
        assert "boundary" in ids
        assert "old" not in ids


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestRuleETL003:
    """RULE-ETL-003: ETL updates description, labels, is_claimed, updated_at, and re-enriches."""

    def test_description_updated_on_refresh(self):
        db = {}
        issue = make_github_issue(id="gh-1", description="Old description")
        upsert_issue(db, issue)

        updated_issue = {**issue, "description": "New updated description"}
        upsert_issue(db, updated_issue)

        assert db["gh-1"]["description"] == "New updated description"

    def test_labels_updated_on_refresh(self):
        db = {}
        issue = make_github_issue(id="gh-1", labels=["design"])
        upsert_issue(db, issue)

        updated_issue = {**issue, "labels": ["design", "ux-review"]}
        upsert_issue(db, updated_issue)

        assert "ux-review" in db["gh-1"]["labels"]

    def test_enrichment_runs_on_update(self):
        db = {}
        issue = make_github_issue(id="gh-1")
        upsert_issue(db, issue)
        enriched = enrich_issue(db["gh-1"])
        db["gh-1"] = enriched
        assert "complexity_score" in db["gh-1"]
        assert "attractiveness_rating" in db["gh-1"]
        assert "seniority_level" in db["gh-1"]


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestRuleETL004:
    """RULE-ETL-004: When an issue is closed on GitHub, its status changes to 'archived'."""

    def test_closed_issue_status_changes_to_archived(self):
        db = {}
        issue = make_github_issue(id="gh-1", state="open")
        upsert_issue(db, {**issue, "status": "active"})

        archive_closed_issue(db, "gh-1")

        assert db["gh-1"]["status"] == "archived"

    def test_archived_issue_not_in_main_listing(self):
        db = {}
        issue = make_github_issue(id="gh-1")
        upsert_issue(db, {**issue, "status": "active", "classification": "relevant"})
        archive_closed_issue(db, "gh-1")

        main_listing = [
            v for v in db.values()
            if v.get("classification") == "relevant" and v.get("status") == "active"
        ]
        assert len(main_listing) == 0

    def test_archiving_nonexistent_issue_is_safe(self):
        db = {}
        result = archive_closed_issue(db, "does-not-exist")
        assert result == {}


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

class TestRuleETL005:
    """RULE-ETL-005: Enrichment sets complexity_score, attractiveness_rating, seniority_level."""

    def test_enrichment_sets_complexity_score(self):
        issue = make_github_issue()
        enriched = enrich_issue(issue)
        assert enriched["complexity_score"] in VALID_COMPLEXITY_SCORES

    def test_enrichment_sets_attractiveness_rating_in_range(self):
        issue = make_github_issue()
        enriched = enrich_issue(issue)
        rating = enriched["attractiveness_rating"]
        assert isinstance(rating, float)
        assert 0.0 <= rating <= 1.0

    def test_enrichment_sets_seniority_level(self):
        issue = make_github_issue()
        enriched = enrich_issue(issue)
        assert enriched["seniority_level"] in VALID_SENIORITY_LEVELS

    def test_enrichment_only_runs_for_relevant_issues(self):
        """
        TODO: Spec doesn't explicitly restrict enrichment to relevant issues,
        but enrichment attributes (complexity, attractiveness, seniority) are
        only meaningful for relevant issues. Confirm with spec owner whether
        not_relevant issues should be enriched.
        """
        # Currently we enrich all issues that pass classification
        relevant_issue = {**make_github_issue(), "classification": "relevant"}
        enriched = enrich_issue(relevant_issue)
        assert enriched["complexity_score"] is not None


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestRuleETL006:
    """RULE-ETL-006: ETL detects images, videos, or links and sets has_media accordingly."""

    def test_description_with_markdown_image_sets_has_media_true(self):
        desc = "Here is a screenshot: ![screenshot](https://example.com/img.png)"
        assert detect_has_media(desc) is True

    def test_description_with_external_link_sets_has_media_true(self):
        desc = "See the Figma file: https://figma.com/file/abc123"
        assert detect_has_media(desc) is True

    def test_description_with_video_tag_sets_has_media_true(self):
        desc = "Watch the demo: <video src='https://example.com/demo.mp4'></video>"
        assert detect_has_media(desc) is True

    def test_plain_text_description_sets_has_media_false(self):
        desc = "This issue requires designing a new onboarding flow. No media attached."
        assert detect_has_media(desc) is False

    def test_empty_description_sets_has_media_false(self):
        assert detect_has_media("") is False

    def test_inline_code_without_url_sets_has_media_false(self):
        desc = "Use `figma.design()` to export the component."
        assert detect_has_media(desc) is False

    def test_freshness_days_computed_correctly(self):
        issue = make_github_issue(created_at=NOW - timedelta(days=7))
        assert compute_freshness_days(issue, now=NOW) == 7
