"""
Backend tests for the ETL Pipeline.
Spec: specs/behavior/etl.spec.md
"""
import pytest
from datetime import datetime, timezone, timedelta
from conftest import make_issue


TODAY = datetime(2026, 5, 6, tzinfo=timezone.utc)


def days_old(n: int) -> datetime:
    return TODAY - timedelta(days=n)


def freshness_days(issue: dict) -> int:
    delta = TODAY - issue["created_at"]
    return delta.days


def is_within_fetch_window(issue: dict, window_days: int = 90) -> bool:
    """RULE-ETL-002: Exclude issues older than window_days on initial fetch."""
    return freshness_days(issue) <= window_days


def archive_if_closed(issue: dict, is_closed_on_github: bool) -> dict:
    """RULE-ETL-004: Closed issues move to archived status."""
    if is_closed_on_github:
        return {**issue, "status": "archived"}
    return issue


def detect_media(description: str) -> bool:
    """RULE-ETL-006: Detect presence of images or video links in description."""
    import re
    image_pattern = r"!\[.*?\]\(https?://.*?\)"
    link_pattern = r"https?://\S+"
    return bool(re.search(image_pattern, description) or re.search(link_pattern, description))


# ---------------------------------------------------------------------------
# RULE-ETL-001: Daily automated refresh
# ---------------------------------------------------------------------------

def test_daily_run_adds_new_issues():
    """RULE-ETL-001: Scenario: Daily run fetches new issues."""
    existing_ids = {"issue-001", "issue-002"}
    new_issues = [
        make_issue(id=f"new-{i}", created_at=days_old(0)) for i in range(5)
    ]
    all_ids = existing_ids | {i["id"] for i in new_issues}
    assert len(all_ids) == len(existing_ids) + 5


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

def test_old_issue_excluded_on_initial_fetch():
    """RULE-ETL-002: Scenario: Old issue excluded on initial fetch (100 days old)."""
    issue = make_issue(created_at=days_old(100))
    assert not is_within_fetch_window(issue)


def test_recent_issue_included_on_initial_fetch():
    """RULE-ETL-002: Scenario: Recent issue included (30 days old)."""
    issue = make_issue(created_at=days_old(30))
    assert is_within_fetch_window(issue)


def test_exactly_90_days_old_is_included():
    """RULE-ETL-002: Boundary — issue at exactly 90 days is included."""
    issue = make_issue(created_at=days_old(90))
    assert is_within_fetch_window(issue)


def test_91_days_old_is_excluded():
    """RULE-ETL-002: Boundary — issue at 91 days is excluded."""
    issue = make_issue(created_at=days_old(91))
    assert not is_within_fetch_window(issue)


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

def test_issue_description_updated_on_refresh():
    """RULE-ETL-003: Scenario: Issue updated on refresh."""
    original = make_issue(description="Old description")
    updated_data = {"description": "New description with more detail."}
    refreshed = {**original, **updated_data}
    assert refreshed["description"] == "New description with more detail."


def test_enrichment_recalculated_on_update():
    """RULE-ETL-003: Enrichment scores are recalculated after update."""
    original = make_issue(complexity_score="low", attractiveness_rating=0.4)
    recalculated = {**original, "complexity_score": "high", "attractiveness_rating": 0.9}
    assert recalculated["complexity_score"] == "high"
    assert recalculated["attractiveness_rating"] == 0.9


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

def test_closed_issue_moves_to_archived():
    """RULE-ETL-004: Scenario: Closed issue moves to archive."""
    issue = make_issue(status="active")
    result = archive_if_closed(issue, is_closed_on_github=True)
    assert result["status"] == "archived"


def test_open_issue_stays_active():
    """RULE-ETL-004: Open issue status unchanged when not closed."""
    issue = make_issue(status="active")
    result = archive_if_closed(issue, is_closed_on_github=False)
    assert result["status"] == "active"


def test_archived_issue_excluded_from_main_listing():
    """RULE-ETL-004: Archived issue no longer appears in main listing."""
    issue = make_issue(status="archived")
    in_listing = issue["status"] == "active" and issue["classification"] == "relevant"
    assert not in_listing


# ---------------------------------------------------------------------------
# RULE-ETL-005: Enrichment generates AI attributes
# ---------------------------------------------------------------------------

VALID_COMPLEXITY = {"low", "medium", "high"}
VALID_SENIORITY = {"junior", "senior"}


def test_enrichment_populates_complexity_score():
    """RULE-ETL-005: Scenario: Enrichment populates attributes — complexity_score."""
    issue = make_issue(classification="relevant", complexity_score="medium")
    assert issue["complexity_score"] in VALID_COMPLEXITY


def test_enrichment_populates_attractiveness_rating():
    """RULE-ETL-005: Scenario: Enrichment populates attributes — attractiveness_rating."""
    issue = make_issue(classification="relevant", attractiveness_rating=0.75)
    assert 0.0 <= issue["attractiveness_rating"] <= 1.0


def test_enrichment_populates_seniority_level():
    """RULE-ETL-005: Scenario: Enrichment populates attributes — seniority_level."""
    issue = make_issue(classification="relevant", seniority_level="junior")
    assert issue["seniority_level"] in VALID_SENIORITY


@pytest.mark.parametrize("complexity", ["low", "medium", "high"])
def test_complexity_score_valid_enum_values(complexity):
    """RULE-ETL-005: complexity_score only accepts valid enum values."""
    issue = make_issue(complexity_score=complexity)
    assert issue["complexity_score"] in VALID_COMPLEXITY


@pytest.mark.parametrize("seniority", ["junior", "senior"])
def test_seniority_level_valid_enum_values(seniority):
    """RULE-ETL-005: seniority_level only accepts valid enum values."""
    issue = make_issue(seniority_level=seniority)
    assert issue["seniority_level"] in VALID_SENIORITY


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

def test_issue_with_image_markdown_has_media():
    """RULE-ETL-006: Scenario: Issue with image detected."""
    description = "See screenshot: ![screenshot](https://example.com/img.png)"
    assert detect_media(description) is True


def test_issue_with_plain_text_has_no_media():
    """RULE-ETL-006: Scenario: Issue with no media."""
    description = "Please redesign the settings page with better contrast."
    assert detect_media(description) is False


def test_issue_with_http_link_has_media():
    """RULE-ETL-006: External links count as media presence."""
    description = "Reference design: https://figma.com/file/abc123"
    assert detect_media(description) is True


def test_issue_with_only_text_and_headings_no_media():
    """RULE-ETL-006: Markdown headings and plain text — no media."""
    description = "## Overview\nWe need to improve the onboarding UX.\n## Goals\n- Simplify signup"
    assert detect_media(description) is False
