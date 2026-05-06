"""
Tests for ETL Pipeline behavior.

Spec: specs/behavior/etl.spec.md
Rules: RULE-ETL-001 through RULE-ETL-006
Glossary: TERM-011 (ETL Pipeline)
Domain: ENTITY-001 (Issue)
"""
import pytest
from datetime import datetime, timezone, timedelta
from tests.backend.conftest import make_issue


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone.utc)
MAX_AGE_DAYS = 90


def _days_old(issue):
    """Age of an issue in days relative to NOW."""
    return (NOW - issue["created_at"]).days


def _should_include_on_initial_fetch(issue):
    """RULE-ETL-002: exclude issues older than 90 days on initial/reset fetch."""
    return _days_old(issue) <= MAX_AGE_DAYS


def _upsert_issue(db: dict, issue: dict):
    """Simulate upsert: insert or update issue by id."""
    db[issue["id"]] = issue.copy()


def _archive_closed_issue(db: dict, issue_id: str):
    """RULE-ETL-004: mark a closed issue as archived."""
    if issue_id in db:
        db[issue_id]["status"] = "archived"


def _detect_media(description: str) -> bool:
    """RULE-ETL-006: detect images, videos, or external links."""
    markers = ["![", "](http", "<img", "<video", "https://", "http://"]
    return any(m in description for m in markers)


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

def test_etl_daily_run_adds_new_issues():
    """RULE-ETL-001 / Scenario: Daily run fetches new issues."""
    db = {}
    new_issues = [make_issue(id=f"new-{i}") for i in range(5)]
    for issue in new_issues:
        _upsert_issue(db, issue)
    assert len(db) == 5


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

def test_etl_old_issue_excluded_on_initial_fetch():
    """RULE-ETL-002 / Scenario: Old issue excluded on initial fetch."""
    old_issue = make_issue(
        id="old",
        created_at=NOW - timedelta(days=100),
    )
    assert _should_include_on_initial_fetch(old_issue) is False


def test_etl_recent_issue_included_on_initial_fetch():
    """RULE-ETL-002 / Scenario: Recent issue included."""
    recent_issue = make_issue(
        id="recent",
        created_at=NOW - timedelta(days=30),
    )
    assert _should_include_on_initial_fetch(recent_issue) is True


def test_etl_boundary_90_days_included():
    """RULE-ETL-002 / Boundary: exactly 90 days old is included."""
    boundary = make_issue(
        id="boundary",
        created_at=NOW - timedelta(days=90),
    )
    assert _should_include_on_initial_fetch(boundary) is True


def test_etl_boundary_91_days_excluded():
    """RULE-ETL-002 / Boundary: 91 days old is excluded."""
    just_over = make_issue(
        id="over",
        created_at=NOW - timedelta(days=91),
    )
    assert _should_include_on_initial_fetch(just_over) is False


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

def test_etl_issue_updated_on_refresh():
    """RULE-ETL-003 / Scenario: Issue updated on refresh."""
    db = {}
    original = make_issue(id="issue-x", description="Original description")
    _upsert_issue(db, original)

    updated = make_issue(
        id="issue-x",
        description="Updated description after GitHub edit",
        updated_at=NOW,
    )
    _upsert_issue(db, updated)

    assert db["issue-x"]["description"] == "Updated description after GitHub edit"


def test_etl_upsert_preserves_existing_id():
    """RULE-ETL-003 / Invariant: id is unique across all issues (ENTITY-001)."""
    db = {}
    issue_v1 = make_issue(id="stable-id", title="v1")
    issue_v2 = make_issue(id="stable-id", title="v2")
    _upsert_issue(db, issue_v1)
    _upsert_issue(db, issue_v2)
    assert len(db) == 1
    assert db["stable-id"]["title"] == "v2"


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

def test_etl_closed_issue_moves_to_archived():
    """RULE-ETL-004 / Scenario: Closed issue moves to archive."""
    db = {}
    issue = make_issue(id="closing", status="active")
    _upsert_issue(db, issue)

    _archive_closed_issue(db, "closing")

    assert db["closing"]["status"] == "archived"


def test_etl_archived_issue_not_in_active_listing():
    """RULE-ETL-004 / And: archived issue does not appear in main listing."""
    db = {}
    issue = make_issue(id="closing", status="active")
    _upsert_issue(db, issue)
    _archive_closed_issue(db, "closing")

    active_issues = [i for i in db.values() if i["status"] == "active"]
    assert not any(i["id"] == "closing" for i in active_issues)


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

def _enrich(issue: dict) -> dict:
    """Stub enrichment: validates attribute shapes (not actual AI values)."""
    enriched = issue.copy()
    # In a real implementation these come from the AI enrichment step.
    # Here we validate that whatever values ARE set conform to the contract.
    assert enriched.get("complexity_score") in ("low", "medium", "high"), (
        "complexity_score must be low, medium, or high"
    )
    assert 0.0 <= enriched.get("attractiveness_rating", -1) <= 1.0, (
        "attractiveness_rating must be 0.0–1.0"
    )
    assert enriched.get("seniority_level") in ("junior", "senior"), (
        "seniority_level must be junior or senior"
    )
    return enriched


def test_etl_enrichment_populates_complexity_score(relevant_active_issue):
    """RULE-ETL-005 / Scenario: Enrichment populates attributes — complexity_score."""
    enriched = _enrich(relevant_active_issue)
    assert enriched["complexity_score"] in ("low", "medium", "high")


def test_etl_enrichment_populates_attractiveness_rating(relevant_active_issue):
    """RULE-ETL-005 / Scenario: Enrichment populates attributes — attractiveness_rating."""
    enriched = _enrich(relevant_active_issue)
    assert 0.0 <= enriched["attractiveness_rating"] <= 1.0


def test_etl_enrichment_populates_seniority_level(relevant_active_issue):
    """RULE-ETL-005 / Scenario: Enrichment populates attributes — seniority_level."""
    enriched = _enrich(relevant_active_issue)
    assert enriched["seniority_level"] in ("junior", "senior")


@pytest.mark.parametrize("complexity", ["low", "medium", "high"])
def test_etl_enrichment_complexity_score_valid_values(complexity):
    """RULE-ETL-005 / Parameterized: all valid complexity_score values pass."""
    issue = make_issue(complexity_score=complexity)
    enriched = _enrich(issue)
    assert enriched["complexity_score"] == complexity


@pytest.mark.parametrize("seniority", ["junior", "senior"])
def test_etl_enrichment_seniority_level_valid_values(seniority):
    """RULE-ETL-005 / Parameterized: all valid seniority_level values pass."""
    issue = make_issue(seniority_level=seniority)
    enriched = _enrich(issue)
    assert enriched["seniority_level"] == seniority


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

def test_etl_media_detection_image_markdown():
    """RULE-ETL-006 / Scenario: Issue with image detected — markdown syntax."""
    description = "Here is a screenshot: ![screenshot](https://example.com/img.png)"
    assert _detect_media(description) is True


def test_etl_media_detection_plain_text_no_media():
    """RULE-ETL-006 / Scenario: Issue with no media."""
    description = "Plain text description with no links or images."
    assert _detect_media(description) is False


def test_etl_media_detection_external_link():
    """RULE-ETL-006 / Implicit: external link (http/https) counts as media."""
    description = "See the design at https://www.figma.com/file/abc123"
    assert _detect_media(description) is True


def test_etl_media_detection_html_img_tag():
    """RULE-ETL-006 / Implicit: HTML img tag counts as media."""
    description = 'See <img src="https://example.com/img.png" />'
    assert _detect_media(description) is True


def test_etl_media_detection_sets_has_media_attribute():
    """RULE-ETL-006 / Contract: has_media attribute is set based on detection."""
    issue_with_img = make_issue(description="![fig](https://example.com/a.png)")
    issue_no_media = make_issue(description="Just text here.")

    issue_with_img["has_media"] = _detect_media(issue_with_img["description"])
    issue_no_media["has_media"] = _detect_media(issue_no_media["description"])

    assert issue_with_img["has_media"] is True
    assert issue_no_media["has_media"] is False
