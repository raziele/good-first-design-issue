"""Tests for RULE-ETL-001 through RULE-ETL-006: ETL Pipeline."""
import pytest
from datetime import datetime, timezone, timedelta
from app.etl import (
    should_include_issue,
    detect_media,
    archive_closed_issue,
    upsert_issue,
)


def _make_raw_issue(created_days_ago: int, state: str = "open", body: str = "") -> dict:
    created_at = datetime.now(timezone.utc) - timedelta(days=created_days_ago)
    return {
        "id": f"github_{created_days_ago}",
        "title": "Some issue",
        "body": body,
        "html_url": "https://github.com/owner/repo/issues/1",
        "state": state,
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
        "comments": [],
    }


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

def test_should_include_issue_old_issue_excluded_on_reset():
    """RULE-ETL-002 — issue created 100 days ago is excluded on initial/reset fetch."""
    issue = _make_raw_issue(created_days_ago=100)
    assert should_include_issue(issue, mode="reset") is False


def test_should_include_issue_recent_included_on_reset():
    """RULE-ETL-002 — issue created 30 days ago is included on initial/reset fetch."""
    issue = _make_raw_issue(created_days_ago=30)
    assert should_include_issue(issue, mode="reset") is True


def test_should_include_issue_boundary_90_days_excluded():
    """RULE-ETL-002 — issue at exactly 90 days boundary is excluded."""
    issue = _make_raw_issue(created_days_ago=90)
    assert should_include_issue(issue, mode="reset") is False


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

def test_archive_closed_issue_changes_status_to_archived():
    """RULE-ETL-004 — closed GitHub issue → status becomes 'archived'."""
    existing_record = {
        "id": "github_1",
        "status": "active",
        "classification": "relevant",
    }
    raw_closed_issue = _make_raw_issue(created_days_ago=5, state="closed")
    result = archive_closed_issue(existing_record, raw_closed_issue)
    assert result["status"] == "archived"


def test_active_issue_stays_active():
    """RULE-ETL-004 — open GitHub issue does not become archived."""
    existing_record = {
        "id": "github_1",
        "status": "active",
        "classification": "relevant",
    }
    raw_open_issue = _make_raw_issue(created_days_ago=5, state="open")
    result = archive_closed_issue(existing_record, raw_open_issue)
    assert result["status"] == "active"


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

def test_detect_media_image_markdown():
    """RULE-ETL-006 — markdown image in body → has_media = True."""
    body = "Here is a screenshot: ![screenshot](https://example.com/image.png)"
    assert detect_media(body) is True


def test_detect_media_plain_text():
    """RULE-ETL-006 — plain text description → has_media = False."""
    body = "This issue is about improving the navigation flow. No images attached."
    assert detect_media(body) is False


def test_detect_media_external_link():
    """RULE-ETL-006 — external link in body → has_media = True."""
    body = "See the design spec at https://figma.com/design/xyz for reference."
    assert detect_media(body) is True


def test_detect_media_video_embed():
    """RULE-ETL-006 — video reference in body → has_media = True."""
    body = "Watch the recording: ![video](https://example.com/video.mp4)"
    assert detect_media(body) is True


def test_detect_media_empty_body():
    """RULE-ETL-006 — empty body → has_media = False."""
    assert detect_media("") is False
