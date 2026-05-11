"""Tests for ETL pipeline rules: RULE-ETL-002, RULE-ETL-004, RULE-ETL-006."""

from __future__ import annotations

import pytest

from app.etl import detect_media, is_within_fetch_window, should_archive_issue


# ---------------------------------------------------------------------------
# RULE-ETL-002: Issues older than 90 days excluded on initial fetch
# ---------------------------------------------------------------------------


def test_issue_older_than_90_days_excluded_on_initial_fetch():
    """RULE-ETL-002 / Scenario: Old issue excluded on initial fetch."""
    assert is_within_fetch_window(days_old=100) is False


def test_issue_within_90_days_included_on_initial_fetch():
    """RULE-ETL-002 / Scenario: Recent issue included."""
    assert is_within_fetch_window(days_old=30) is True


def test_issue_exactly_90_days_is_included():
    """RULE-ETL-002 / Boundary: exactly 90 days is on the edge — included."""
    assert is_within_fetch_window(days_old=90) is True


def test_issue_91_days_is_excluded():
    """RULE-ETL-002 / Boundary: 91 days is beyond the window."""
    assert is_within_fetch_window(days_old=91) is False


# ---------------------------------------------------------------------------
# RULE-ETL-004: Closed issues are archived
# ---------------------------------------------------------------------------


def test_closed_issue_should_be_archived():
    """RULE-ETL-004 / Scenario: Closed issue moves to archive."""
    assert should_archive_issue(github_state="closed") is True


def test_open_issue_should_not_be_archived():
    """RULE-ETL-004 / Open issues stay active."""
    assert should_archive_issue(github_state="open") is False


# ---------------------------------------------------------------------------
# RULE-ETL-006: Media detection
# ---------------------------------------------------------------------------


def test_description_with_markdown_image_sets_has_media():
    """RULE-ETL-006 / Scenario: Issue with image detected."""
    assert detect_media("Here is a screenshot: ![screenshot](https://example.com/img.png)") is True


def test_description_with_html_img_sets_has_media():
    """RULE-ETL-006 / HTML img tag also counts as media."""
    assert detect_media('<img src="https://example.com/photo.jpg" />') is True


def test_description_with_video_link_sets_has_media():
    """RULE-ETL-006 / Video link counts as media."""
    assert detect_media("Watch the video: https://www.youtube.com/watch?v=abc") is True


def test_plain_text_description_no_media():
    """RULE-ETL-006 / Scenario: Issue with no media."""
    assert detect_media("This is a plain text description with no links or images.") is False


def test_empty_description_no_media():
    """RULE-ETL-006 / Empty description has no media."""
    assert detect_media("") is False
