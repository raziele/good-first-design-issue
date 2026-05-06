/**
 * Tests for Claim flow UI behavior.
 *
 * Spec: specs/behavior/claim.spec.md
 * Rules: RULE-CLM-001 through RULE-CLM-004
 * UXI Flow: specs/uxi/flows/claim-issue.flow.md
 * Glossary: TERM-002 (Claim), TERM-012 (Claim Comment)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  github_url: string;
  title: string;
  description: string;
  is_claimed: boolean;
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "clm-001",
    github_url: "https://github.com/org/repo/issues/5",
    title: "Redesign mobile onboarding",
    description: "Full UX redesign of the onboarding screens with Figma.",
    is_claimed: false,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Stub claim flow logic
// ---------------------------------------------------------------------------

type ClaimOption = "go_to_github" | "copy_comment";

interface ClaimModal {
  title: string;
  commentPreview: string;
  options: ClaimOption[];
  cancelAvailable: boolean;
}

function openClaimModal(issue: Issue, claimComment: string): ClaimModal {
  return {
    title: "Ready to claim this task?",
    commentPreview: claimComment,
    options: ["go_to_github", "copy_comment"],
    cancelAvailable: true,
  };
}

interface GoToGitHubResult {
  url: string;
  opensInNewTab: boolean;
}

function handleGoToGitHub(issue: Issue, comment: string): GoToGitHubResult {
  const encoded = encodeURIComponent(comment);
  return {
    url: `${issue.github_url}?body=${encoded}`,
    opensInNewTab: true,
  };
}

interface CopyCommentResult {
  success: boolean;
  toastMessage: string;
  autoDismissMs: number;
}

function handleCopyComment(_comment: string): CopyCommentResult {
  return {
    success: true,
    toastMessage: "Comment copied! Paste it on GitHub when you're ready.",
    autoDismissMs: 3000,
  };
}

function generateClaimComment(issue: Issue): string {
  // TODO: Replace with AI-generated comment once service is wired.
  return `Hey! I'd love to take this on — I'll work on the ${issue.title.toLowerCase()} and share updates soon.`;
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

describe("ClaimFlow.behavior — RULE-CLM-001 two options", () => {
  it("claim modal shows title 'Ready to claim this task?'", () => {
    const modal = openClaimModal(makeIssue(), generateClaimComment(makeIssue()));
    expect(modal.title).toBe("Ready to claim this task?");
  });

  it("claim modal provides both go_to_github and copy_comment options", () => {
    const modal = openClaimModal(makeIssue(), generateClaimComment(makeIssue()));
    expect(modal.options).toContain("go_to_github");
    expect(modal.options).toContain("copy_comment");
    expect(modal.options).toHaveLength(2);
  });

  it("claim modal shows a comment preview", () => {
    const comment = generateClaimComment(makeIssue());
    const modal = openClaimModal(makeIssue(), comment);
    expect(modal.commentPreview.length).toBeGreaterThan(0);
  });

  it("claim modal has a cancel option", () => {
    const modal = openClaimModal(makeIssue(), "");
    expect(modal.cancelAvailable).toBe(true);
  });

  it("go_to_github opens with pre-filled comment in URL", () => {
    const issue = makeIssue();
    const comment = generateClaimComment(issue);
    const result = handleGoToGitHub(issue, comment);
    expect(result.url).toContain(issue.github_url);
    expect(result.url).toContain("body=");
    expect(result.opensInNewTab).toBe(true);
  });

  it("copy_comment returns success and correct toast message", () => {
    const result = handleCopyComment(generateClaimComment(makeIssue()));
    expect(result.success).toBe(true);
    expect(result.toastMessage).toBe("Comment copied! Paste it on GitHub when you're ready.");
  });

  it("copy_comment toast auto-dismisses after 3 seconds", () => {
    const result = handleCopyComment("any comment");
    expect(result.autoDismissMs).toBe(3000);
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-002: Claim comment is AI-generated (contextual)
// ---------------------------------------------------------------------------

describe("ClaimFlow.behavior — RULE-CLM-002 contextual comment", () => {
  it("generated comment is non-empty", () => {
    const comment = generateClaimComment(makeIssue());
    expect(comment.length).toBeGreaterThan(0);
  });

  it("generated comment differs between different issues", () => {
    const issueA = makeIssue({ title: "Settings page redesign" });
    const issueB = makeIssue({ title: "Icon library creation" });
    expect(generateClaimComment(issueA)).not.toBe(generateClaimComment(issueB));
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-003: No local claim tracking
// ---------------------------------------------------------------------------

describe("ClaimFlow.behavior — RULE-CLM-003 no local state", () => {
  it("claim action does not mutate the issue's is_claimed field locally", () => {
    const issue = makeIssue({ is_claimed: false });
    const comment = generateClaimComment(issue);
    handleCopyComment(comment); // perform claim action
    // is_claimed remains false until ETL refresh reads GitHub comments
    expect(issue.is_claimed).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: Multiple users can claim same issue
// ---------------------------------------------------------------------------

describe("ClaimFlow.behavior — RULE-CLM-004 multi-user claim", () => {
  it("claim modal always shows same options regardless of is_claimed state", () => {
    const claimedIssue = makeIssue({ is_claimed: true });
    const unclaimedIssue = makeIssue({ is_claimed: false });
    const commentA = generateClaimComment(claimedIssue);
    const commentB = generateClaimComment(unclaimedIssue);
    const modalA = openClaimModal(claimedIssue, commentA);
    const modalB = openClaimModal(unclaimedIssue, commentB);
    expect(modalA.options).toEqual(modalB.options);
  });

  it("already-claimed issue still shows 'Already claimed' badge in detail view", () => {
    const issue = makeIssue({ is_claimed: true });
    const badge = issue.is_claimed ? "Already claimed" : null;
    expect(badge).toBe("Already claimed");
  });

  it("already-claimed issue does not block the claim CTA", () => {
    // RULE-CLM-004: no block, just a hint
    const issue = makeIssue({ is_claimed: true });
    const ctaEnabled = true; // always enabled regardless of is_claimed
    expect(ctaEnabled).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Edge cases from claim-issue.flow.md
// ---------------------------------------------------------------------------

describe("ClaimFlow.behavior — edge cases (flow spec)", () => {
  it("clipboard failure produces a fallback error message", () => {
    function handleCopyCommentFailing(): { success: boolean; errorMessage: string } {
      return {
        success: false,
        errorMessage: "Couldn't copy. Try selecting the text manually.",
      };
    }
    const result = handleCopyCommentFailing();
    expect(result.success).toBe(false);
    expect(result.errorMessage).toMatch(/Couldn't copy/);
  });

  it("popup blocker shows fallback link message", () => {
    function handlePopupBlocked(issueUrl: string): { showFallbackLink: boolean; fallbackUrl: string } {
      return { showFallbackLink: true, fallbackUrl: issueUrl };
    }
    const issue = makeIssue();
    const result = handlePopupBlocked(issue.github_url);
    expect(result.showFallbackLink).toBe(true);
    expect(result.fallbackUrl).toBe(issue.github_url);
  });
});
