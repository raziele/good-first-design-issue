"""Issue browsing rules: RULE-ISS-001, RULE-ISS-002, RULE-ISS-005."""

from __future__ import annotations

from typing import Any


def filter_listable_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """RULE-ISS-001: Return only relevant active issues."""
    return [
        issue for issue in issues
        if issue.get("classification") == "relevant" and issue.get("status") == "active"
    ]


def sort_issues_by_freshness(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """RULE-ISS-005: Sort issues by freshness_days ascending (newest first)."""
    return sorted(issues, key=lambda i: i.get("freshness_days", 0))


def truncate_description(description: str, max_length: int = 200) -> str:
    """RULE-ISS-002: Truncate description to max_length chars, appending ellipsis if trimmed."""
    if len(description) <= max_length:
        return description
    return description[: max_length - 3] + "..."
