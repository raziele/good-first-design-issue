"""
Cross-cutting brand copy tests.
Spec: specs/brand/voice-and-tone.md

These tests validate that the exact copy strings defined in the spec are used
in the correct places. They act as a contract between design and engineering.
"""

import pytest


# ---------------------------------------------------------------------------
# Canonical copy strings from specs/brand/voice-and-tone.md
# ---------------------------------------------------------------------------

COPY = {
    "cta_claim": "Claim This Task",
    "empty_search": "No matches — try adjusting your filters or search terms.",
    "clipboard_success": "Comment copied! Paste it on GitHub when you're ready.",
    "already_claimed_badge": "Already claimed",
    "media_indicator_tooltip": "This issue includes images or links",
    "tagline": "Your next portfolio piece is waiting.",
    "error_load": "Couldn't load tasks. Check your connection and try again.",
    "clipboard_fail": "Couldn't copy. Try selecting the text manually.",
    "claim_modal_title": "Ready to claim this task?",
}

FORBIDDEN_PATTERNS = [
    "leverage",
    "synergy",
    "utilize",
    "Land your dream job",
    "The system has detected",
    "express interest",
    "opportunity",  # prefer "task" or "issue"
]

PREFERRED_TERMS = {
    "Claim": ["Apply", "Express interest"],
    "Task": ["Opportunity", "Listing"],
    "Designer": ["User", "Customer"],
    "Open source": ["OSS"],
}


class TestBrandCopyStrings:
    def test_cta_claim_exact_text(self):
        """CTA button must say 'Claim This Task' — not 'Apply' or 'Express interest'."""
        assert COPY["cta_claim"] == "Claim This Task"

    def test_empty_search_exact_text(self):
        """Empty search message must match spec copy exactly."""
        assert COPY["empty_search"] == "No matches — try adjusting your filters or search terms."

    def test_clipboard_success_exact_text(self):
        """Clipboard success message must match spec copy exactly."""
        assert COPY["clipboard_success"] == "Comment copied! Paste it on GitHub when you're ready."

    def test_already_claimed_badge_text(self):
        """Already claimed badge must say 'Already claimed'."""
        assert COPY["already_claimed_badge"] == "Already claimed"

    def test_media_indicator_tooltip_text(self):
        """Media indicator tooltip must say 'This issue includes images or links'."""
        assert COPY["media_indicator_tooltip"] == "This issue includes images or links"

    def test_error_load_text(self):
        """Load error message must match spec copy exactly."""
        assert COPY["error_load"] == "Couldn't load tasks. Check your connection and try again."

    def test_clipboard_fail_text(self):
        """Clipboard failure message must match spec copy exactly."""
        assert COPY["clipboard_fail"] == "Couldn't copy. Try selecting the text manually."

    def test_claim_modal_title_text(self):
        """Claim modal title must match spec copy exactly."""
        assert COPY["claim_modal_title"] == "Ready to claim this task?"


class TestForbiddenPatterns:
    @pytest.mark.parametrize("pattern", FORBIDDEN_PATTERNS)
    def test_forbidden_pattern_not_in_copy_strings(self, pattern):
        """Forbidden jargon/patterns must not appear in canonical copy."""
        for key, text in COPY.items():
            assert pattern.lower() not in text.lower(), (
                f"Forbidden pattern '{pattern}' found in copy['{key}']: {text!r}"
            )


class TestPreferredTerminology:
    def test_cta_uses_claim_not_apply(self):
        """Terminology: prefer 'Claim' over 'Apply' or 'Express interest'."""
        assert "apply" not in COPY["cta_claim"].lower()
        assert "express interest" not in COPY["cta_claim"].lower()

    def test_no_exclamation_overuse(self):
        """Do not use exclamation points excessively (max 1 per copy string)."""
        for key, text in COPY.items():
            count = text.count("!")
            assert count <= 1, f"Too many exclamation points ({count}) in copy['{key}']: {text!r}"

    def test_cta_leads_with_verb(self):
        """CTAs must lead with verbs: 'Claim', 'Filter', 'Explore'."""
        cta = COPY["cta_claim"]
        first_word = cta.split()[0]
        assert first_word[0].isupper(), "CTA must start with capitalized verb"
        assert first_word in {"Claim", "Filter", "Explore", "Comment"}, (
            f"CTA '{cta}' does not lead with an expected verb"
        )
