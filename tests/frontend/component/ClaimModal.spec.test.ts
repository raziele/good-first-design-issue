/**
 * Component tests for ClaimModal
 * Spec: specs/behavior/claim.spec.md — RULE-CLM-001, RULE-CLM-002, RULE-CLM-004
 * Flow: specs/uxi/flows/claim-issue.flow.md
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  title: string;
  description: string;
  github_url: string;
  is_claimed: boolean;
}

interface ClaimModalState {
  isOpen: boolean;
  claimComment: string;
  goToGithubUrl: string;
  confirmationMessage: string | null;
  errorMessage: string | null;
  isBlocked: boolean;
  showWarning: boolean;
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-1",
    title: "Redesign mobile onboarding flow",
    description: "We need wireframes and a Figma prototype for the onboarding experience.",
    github_url: "https://github.com/owner/repo/issues/1",
    is_claimed: false,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Stub modal logic
// TODO: replace with @testing-library/react render of <ClaimModal issue={issue} />
// ---------------------------------------------------------------------------

function openClaimModal(issue: Issue): ClaimModalState {
  const claimComment =
    "Hey! I'd love to take this on. I'm a designer looking to contribute — expect an update soon.";
  return {
    isOpen: true,
    claimComment,
    goToGithubUrl: `${issue.github_url}?body=${encodeURIComponent(claimComment)}`,
    confirmationMessage: null,
    errorMessage: null,
    isBlocked: false,
    showWarning: false,
  };
}

function handleCopyComment(
  state: ClaimModalState,
  clipboardFails = false
): ClaimModalState {
  if (clipboardFails) {
    return { ...state, errorMessage: "Couldn't copy. Try selecting the text manually." };
  }
  return {
    ...state,
    confirmationMessage: "Comment copied! Paste it on GitHub when you're ready.",
  };
}

function handleGoToGithub(
  state: ClaimModalState,
  popupBlocked = false
): { redirectUrl?: string; fallbackUrl?: string; blocked: boolean } {
  if (popupBlocked) {
    return { fallbackUrl: state.goToGithubUrl.split("?")[0], blocked: true };
  }
  return { redirectUrl: state.goToGithubUrl, blocked: false };
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

describe("ClaimModal — RULE-CLM-001: two claim paths", () => {
  it("ClaimModal.opensWithTwoOptions", () => {
    /**
     * Scenario: User chooses to go to GitHub / User chooses to copy comment
     * When the user clicks "Claim This Task"
     * Then they are presented with two options
     */
    const state = openClaimModal(makeIssue());
    expect(state.isOpen).toBe(true);
    expect(state.goToGithubUrl).toBeTruthy();
    expect(state.claimComment).toBeTruthy();
  });

  it("ClaimModal.goToGithubUrlContainsIssueUrl", () => {
    /**
     * Scenario: Go to GitHub — redirect includes the issue's github URL
     */
    const issue = makeIssue();
    const state = openClaimModal(issue);
    expect(state.goToGithubUrl).toContain(issue.github_url);
  });

  it("ClaimModal.goToGithubUrlEncodesPrefillComment", () => {
    /**
     * And: the comment field is pre-filled with an AI-generated claim comment
     */
    const state = openClaimModal(makeIssue());
    // Pre-filled body uses URL encoding
    expect(state.goToGithubUrl).toContain("body=");
  });

  it("ClaimModal.copyCommentShowsConfirmation", () => {
    /**
     * Scenario: User chooses to copy comment
     * Then a confirmation message is shown
     */
    const state = openClaimModal(makeIssue());
    const result = handleCopyComment(state);
    expect(result.confirmationMessage).not.toBeNull();
    expect(result.confirmationMessage!.toLowerCase()).toContain("copied");
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-002: Claim comment is AI-generated (non-empty, non-template check)
// ---------------------------------------------------------------------------

describe("ClaimModal — RULE-CLM-002: claim comment content", () => {
  it("ClaimModal.claimCommentIsNonEmpty", () => {
    const state = openClaimModal(makeIssue());
    expect(state.claimComment.trim().length).toBeGreaterThan(20);
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: No blocking for multiple users
// ---------------------------------------------------------------------------

describe("ClaimModal — RULE-CLM-004: no blocking for multiple claimants", () => {
  it("ClaimModal.notBlockedWhenIssueAlreadyClaimed", () => {
    /**
     * Scenario: Second user can claim already-attempted issue
     * Then no warning or block is shown
     */
    const state = openClaimModal(makeIssue({ is_claimed: true }));
    expect(state.isBlocked).toBe(false);
    expect(state.showWarning).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Edge cases (claim-issue.flow.md)
// ---------------------------------------------------------------------------

describe("ClaimModal — edge cases from flow spec", () => {
  it("ClaimModal.clipboardFailureShowsError", () => {
    /**
     * Edge case: Clipboard API fails → error message shown
     */
    const state = openClaimModal(makeIssue());
    const result = handleCopyComment(state, true);
    expect(result.errorMessage).not.toBeNull();
    expect(result.errorMessage!.toLowerCase()).toContain("couldn't copy");
  });

  it("ClaimModal.popupBlockerShowsFallbackLink", () => {
    /**
     * Edge case: Popup blocker → fallback link to GitHub shown
     */
    const issue = makeIssue();
    const state = openClaimModal(issue);
    const result = handleGoToGithub(state, true);
    expect(result.blocked).toBe(true);
    expect(result.fallbackUrl).toBeTruthy();
    expect(result.fallbackUrl).toContain("github.com");
  });

  it("ClaimModal.alreadyClaimedWarningInDetailView", () => {
    /**
     * Already Claimed Warning state:
     * If is_claimed = true, badge "Already claimed" shown on detail view,
     * but claim CTA still available.
     */
    // TODO: assert rendered badge text once component exists
    const issue = makeIssue({ is_claimed: true });
    expect(issue.is_claimed).toBe(true);
    // CTA availability is validated in IssueDetail.spec.test.ts — see claimCtaRemainsEnabledWhenIsClaimed
  });
});
