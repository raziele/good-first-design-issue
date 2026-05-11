"""ETL pipeline rules: RULE-ETL-002, RULE-ETL-004, RULE-ETL-006."""

from __future__ import annotations

import re

_FETCH_WINDOW_DAYS = 90

_MEDIA_PATTERNS = re.compile(
    r"!\[.*?\]\(https?://\S+\)"          # Markdown image
    r"|<img\s[^>]*>"                      # HTML img tag
    r"|https?://(?:www\.)?"
    r"(?:youtube\.com/watch|youtu\.be/|vimeo\.com/)\S+",  # Video links
    re.IGNORECASE,
)


def detect_media(description: str) -> bool:
    """RULE-ETL-006: Return True if description contains image or video media."""
    return bool(_MEDIA_PATTERNS.search(description))


def is_within_fetch_window(*, days_old: int) -> bool:
    """RULE-ETL-002: Return True if an issue is within the 90-day fetch window."""
    return days_old <= _FETCH_WINDOW_DAYS


def should_archive_issue(*, github_state: str) -> bool:
    """RULE-ETL-004: Return True if a closed GitHub issue should be archived."""
    return github_state == "closed"
