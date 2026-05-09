"""
Tests for RULE-ETL-001 through RULE-ETL-006: ETL pipeline behavior.
SUT: app.etl
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.etl import (
    is_within_fetch_window,
    detect_media,
    archive_closed_issue,
    should_update_issue,
)


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------

class TestFetchWindow:
    def test_issue_older_than_90_days_excluded(self):
        """RULE-ETL-002: Issue created 100 days ago is excluded on initial fetch."""
        now = datetime(2026, 5, 9, tzinfo=timezone.utc)
        created_at = now - timedelta(days=100)
        assert is_within_fetch_window(created_at, reference_date=now, max_days=90) is False

    def test_issue_within_90_days_included(self):
        """RULE-ETL-002: Issue created 30 days ago is included on initial fetch."""
        now = datetime(2026, 5, 9, tzinfo=timezone.utc)
        created_at = now - timedelta(days=30)
        assert is_within_fetch_window(created_at, reference_date=now, max_days=90) is True

    def test_issue_exactly_at_90_days_included(self):
        """RULE-ETL-002: Issue created exactly 90 days ago is on the boundary (included)."""
        now = datetime(2026, 5, 9, tzinfo=timezone.utc)
        created_at = now - timedelta(days=90)
        assert is_within_fetch_window(created_at, reference_date=now, max_days=90) is True


# ---------------------------------------------------------------------------
# RULE-ETL-003: Existing issues are updated
# ---------------------------------------------------------------------------

class TestIssueUpdate:
    def test_issue_with_changed_description_should_update(self):
        """RULE-ETL-003: An existing issue with a new description should be updated."""
        existing = {"id": "123", "description": "Old description", "updated_at": "2026-01-01T00:00:00Z"}
        incoming = {"id": "123", "description": "New description", "updated_at": "2026-05-01T00:00:00Z"}
        assert should_update_issue(existing, incoming) is True

    def test_issue_with_same_updated_at_should_not_update(self):
        """RULE-ETL-003: An existing issue with unchanged updated_at does not require update."""
        existing = {"id": "123", "description": "Same", "updated_at": "2026-05-01T00:00:00Z"}
        incoming = {"id": "123", "description": "Same", "updated_at": "2026-05-01T00:00:00Z"}
        assert should_update_issue(existing, incoming) is False


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------

class TestArchiveClosedIssue:
    def test_closed_issue_status_becomes_archived(self):
        """RULE-ETL-004: A closed GitHub issue gets status='archived'."""
        issue = {"id": "42", "status": "active", "github_state": "closed"}
        updated = archive_closed_issue(issue)
        assert updated["status"] == "archived"

    def test_open_issue_status_unchanged(self):
        """RULE-ETL-004: An open GitHub issue keeps status='active'."""
        issue = {"id": "42", "status": "active", "github_state": "open"}
        updated = archive_closed_issue(issue)
        assert updated["status"] == "active"


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------

class TestMediaDetection:
    def test_description_with_image_markdown_has_media(self):
        """RULE-ETL-006: Description with image markdown sets has_media=True."""
        description = "Please see the attached screenshot:\n![screenshot](https://example.com/img.png)"
        assert detect_media(description) is True

    def test_description_with_plain_text_has_no_media(self):
        """RULE-ETL-006: Plain text description sets has_media=False."""
        description = "This is a plain text description with no images or links."
        assert detect_media(description) is False

    def test_description_with_video_link_has_media(self):
        """RULE-ETL-006: Description with external video link sets has_media=True."""
        description = "Watch this video: https://www.loom.com/share/abc123"
        assert detect_media(description) is True

    def test_empty_description_has_no_media(self):
        """RULE-ETL-006: Empty description sets has_media=False."""
        assert detect_media("") is False
