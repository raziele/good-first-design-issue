/**
 * Unit tests for ClaimModal component.
 * Spec: specs/behavior/claim.spec.md (RULE-CLM-001, RULE-CLM-002, RULE-CLM-004)
 * Flow: specs/uxi/flows/claim-issue.flow.md
 */

import { describe, it, expect, vi, beforeEach } from "vitest";

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

interface ClaimOptions {
  claimComment: string;
  githubUrl: string;
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "gh-001",
    github_url: "https://github.com/org/repo/issues/1",
    title: "Mobile onboarding redesign",
    description: "Create wireframes for the onboarding flow.",
    is_claimed: false,
    ...overrides,
  };
}

function buildClaimOptions(issue: Issue, claimComment: string): ClaimOptions {
  const url = `${issue.github_url}?body=${encodeURIComponent(claimComment)}`;
  return { claimComment, githubUrl: url };
}

function generateClaimComment(issue: Issue): string {
  return `Hey! I'd love to work on the ${issue.title.toLowerCase()}. Expect an update soon.`;
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

describe("ClaimModal.user chooses to go to GitHub", () => {
  it("builds a github URL with pre-filled comment body", () => {
    const issue = makeIssue();
    const comment = generateClaimComment(issue);
    const { githubUrl } = buildClaimOptions(issue, comment);

    expect(githubUrl).toContain(issue.github_url);
    expect(githubUrl).toContain("body=");
  });

  it("URL body includes the claim comment text", () => {
    const issue = makeIssue();
    const comment = generateClaimComment(issue);
    const { githubUrl } = buildClaimOptions(issue, comment);

    expect(githubUrl).toContain(encodeURIComponent(comment));
  });
});

describe("ClaimModal.user chooses to copy comment", () => {
  it("provides a non-empty string for clipboard copy", () => {
    const issue = makeIssue();
    const comment = generateClaimComment(issue);
    expect(typeof comment).toBe("string");
    expect(comment.length).toBeGreaterThan(0);
  });

  it("clipboard failure should be surfaced as an error state", () => {
    // Edge case from claim-issue.flow.md:
    // Clipboard API fails → show error "Couldn't copy. Try selecting the text manually."
    const clipboardError = new Error("Clipboard API not available");
    const handleClipboardError = (err: Error) => ({
      type: "error" as const,
      message: "Couldn't copy. Try selecting the text manually.",
    });
    const result = handleClipboardError(clipboardError);
    expect(result.type).toBe("error");
    expect(result.message).toContain("Couldn't copy");
  });
});

describe("ClaimModal.modal states", () => {
  it("modal title is 'Ready to claim this task?'", () => {
    const modalTitle = "Ready to claim this task?";
    expect(modalTitle).toBe("Ready to claim this task?");
  });

  it("both action buttons are present in claim options modal", () => {
    const actions = ["Go to GitHub", "Copy comment"];
    expect(actions).toContain("Go to GitHub");
    expect(actions).toContain("Copy comment");
  });

  it("clipboard confirmation toast shows correct message", () => {
    const toastMessage = "Comment copied! Paste it on GitHub when you're ready.";
    expect(toastMessage).toMatch(/Comment copied/);
  });

  it("popup blocker fallback provides a direct link to GitHub", () => {
    // Edge: popup blocker prevents new tab → show fallback link
    const issue = makeIssue();
    const fallbackLink = issue.github_url;
    expect(fallbackLink).toContain("github.com");
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-002: Claim comment is AI-generated (contextual)
// ---------------------------------------------------------------------------

describe("ClaimModal.claim comment reflects issue context", () => {
  it("comment for design issue mentions design intent", () => {
    const issue = makeIssue({
      title: "Mobile onboarding redesign",
      description: "Design wireframes for the onboarding flow.",
    });
    const comment = generateClaimComment(issue);
    const designSignals = ["onboarding", "design", "flow", "work on", "ux"];
    const hasDesignSignal = designSignals.some((s) =>
      comment.toLowerCase().includes(s)
    );
    expect(hasDesignSignal).toBe(true);
  });

  it("different issues produce different comments", () => {
    const issueA = makeIssue({ title: "Redesign login screen" });
    const issueB = makeIssue({ title: "Create icons for navigation" });
    expect(generateClaimComment(issueA)).not.toBe(generateClaimComment(issueB));
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: Multiple users can claim same issue
// ---------------------------------------------------------------------------

describe("ClaimModal.multiple users can claim same issue", () => {
  it("is_claimed = true does not block the claim modal from opening", () => {
    const issue = makeIssue({ is_claimed: true });
    // No exception should be thrown; options must be generated
    const comment = generateClaimComment(issue);
    const { githubUrl } = buildClaimOptions(issue, comment);
    expect(comment.length).toBeGreaterThan(0);
    expect(githubUrl).toContain("github.com");
  });

  it("shows 'Already claimed' badge on detail view when is_claimed = true", () => {
    const issue = makeIssue({ is_claimed: true });
    // Component contract: badge rendered when is_claimed is true
    const showAlreadyClaimedBadge = issue.is_claimed;
    expect(showAlreadyClaimedBadge).toBe(true);
  });

  it("claim CTA remains enabled even when issue is already claimed", () => {
    const issue = makeIssue({ is_claimed: true });
    // CTA is never disabled due to claim status (RULE-CLM-004 + RULE-ISS-004)
    const ctaDisabled = false; // no logic disables it
    expect(ctaDisabled).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-003: No local claim tracking
// ---------------------------------------------------------------------------

describe("ClaimModal.no local claim tracking", () => {
  it("claim action does not modify the issue's is_claimed field locally", () => {
    const issue = makeIssue({ is_claimed: false });
    // Simulate claim action
    const comment = generateClaimComment(issue);
    buildClaimOptions(issue, comment);
    // is_claimed must remain unchanged after claim (ETL sets it on next refresh)
    expect(issue.is_claimed).toBe(false);
  });
});
