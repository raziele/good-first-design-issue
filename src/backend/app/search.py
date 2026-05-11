"""Search and filtering rules: RULE-SRC-001, RULE-SRC-002, RULE-SRC-003."""

from __future__ import annotations

from typing import Any

_FRESHNESS_MAP = {
    "last_7_days": 7,
    "last_30_days": 30,
    "last_90_days": 90,
}


def search_and_filter_issues(
    issues: list[dict[str, Any]],
    *,
    query: str = "",
    freshness_filter: str = "all_time",
) -> list[dict[str, Any]]:
    """RULE-SRC-001/002/003: Full-text search + freshness filter with AND logic."""
    result = issues

    if query:
        q = query.lower()
        result = [
            i for i in result
            if q in i.get("title", "").lower() or q in i.get("description", "").lower()
        ]

    if freshness_filter and freshness_filter != "all_time":
        max_days = _FRESHNESS_MAP.get(freshness_filter)
        if max_days is not None:
            result = [i for i in result if i.get("freshness_days", 0) <= max_days]

    return result
