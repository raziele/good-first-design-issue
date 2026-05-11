"""Issue classification rules: RULE-CLS-001..004."""

from __future__ import annotations

import re

# Design-related keywords that signal relevance
_DESIGN_KEYWORDS = re.compile(
    r"\b(design|wireframe|mockup|figma|prototype|ui|ux|layout|visual|"
    r"typography|color|icon|illustration|animation|onboarding|flow|"
    r"sketch|adobe|branding|logo|style\s*guide|component|interface)\b",
    re.IGNORECASE,
)

# Exclusion patterns — if matched, the issue is not relevant
_EXCLUSION_PATTERNS = re.compile(
    r"\b(test|qa|unit\s+test|coverage|api|endpoint|backend|database|"
    r"migration|refactor|rename|code\s+base|codebase|utf|sprite|assets?|"
    r"implementation|implement|game)\b",
    re.IGNORECASE,
)

# Markdown section headers that, when they are the only content, indicate a placeholder
_PLACEHOLDER_RE = re.compile(
    r"^(\s*##\s+\w[\w\s]*\n?)+\s*$"
)


def classify_issue(*, title: str, description: str) -> str:
    """RULE-CLS-001: Classify an issue as 'relevant' or 'not_relevant'.

    - RULE-CLS-002: Empty or placeholder-only descriptions are not relevant.
    - RULE-CLS-004: Issues matching exclusion patterns are not relevant.
    """
    stripped = description.strip()

    # RULE-CLS-002: empty or placeholder-only
    if not stripped or _PLACEHOLDER_RE.match(stripped):
        return "not_relevant"

    combined = f"{title} {description}"

    # RULE-CLS-004: exclusion patterns override design signals
    if _EXCLUSION_PATTERNS.search(combined):
        return "not_relevant"

    # RULE-CLS-001: must have at least one design keyword
    if _DESIGN_KEYWORDS.search(combined):
        return "relevant"

    return "not_relevant"
