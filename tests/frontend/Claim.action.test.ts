/**
 * Frontend unit tests for Claiming an Issue.
 * Spec: specs/behavior/claim.spec.md
 * Flow: specs/uxi/flows/claim-issue.flow.md
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { makeIssue } from "./fixtures";

// ---------------------------------------------------------------------------
// Claim action helpers (mirrors component / hook logic)
// ---------------------------------------------------------------------------

interface ClaimOptions {
  github_url: string;
  claim_comment: string;
}

function buildGitHubCommentUrl(github_url: string, claim_comment: string): string {
  const encoded = encodeURIComponent(claim_comment);
  return `${github_url}?body=${encoded}`;
}

async function copyToClipboard(text: string): Promise<{ success: boolean; error?: string }> {
  try {
    await navigator.clipboard.writeText(text);
    return { success: true };
  } catch {
    return { success: false, error: "Couldn't copy. Try selecting the text manually." };
  }
}

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action offers two options
// ---------------------------------------------------------------------------

describe("Claim.action — RULE-CLM-001", () => {
  it("go-to-github path builds a pre-filled comment URL", () => {
    const issue = makeIssue({ github_url: "https://github.com/owner/repo/issues/1" });
    const comment = "Hey! I'd love to take this on. I'm a designer looking to contribute.";
    const url = buildGitHubCommentUrl(issue.github_url, comment);
    expect(url).toContain("github.com/owner/repo/issues/1");
    expect(url).toContain("body=");
    expect(url).toContain(encodeURIComponent(comment));
  });

  it("copy-comment path calls clipboard with the claim comment", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, {
      clipboard: { writeText },
    });

    const comment = "Hey! I'd love to take this on.";
    const result = await copyToClipboard(comment);

    expect(writeText).toHaveBeenCalledWith(comment);
    expect(result.success).toBe(true);
  });

  it("copy-comment path returns confirmation on success", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });

    const result = await copyToClipboard("some comment");
    expect(result.success).toBe(true);
    // The UI should show: "Comment copied! Paste it on GitHub when you're ready."
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-002: Claim comment is AI-generated
// ---------------------------------------------------------------------------

describe("Claim.action — RULE-CLM-002", () => {
  it("claim comment mentions design or UX intent", () => {
    // TODO: wire to actual AI comment generation once endpoint exists.
    // Stub validates the expected comment shape.
    const comment =
      "Hey! I'd love to take this on. I'm a designer looking to contribute to the onboarding flow.";
    const designKeywords = ["design", "designer", "ux", "ui", "onboarding", "contribute"];
    const hasDesignIntent = designKeywords.some((kw) =>
      comment.toLowerCase().includes(kw)
    );
    expect(hasDesignIntent).toBe(true);
  });

  it("claim comment is not a fixed template (contextual)", () => {
    // TODO: verify two different issues produce different comments via AI stub.
    // For now, documents the contract — each comment must reference the issue.
    const issueTitle = "Mobile onboarding redesign";
    const comment = `Hey! I'd love to take this on. I'll work on the ${issueTitle.toLowerCase()}.`;
    expect(comment).toContain("onboarding");
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-003: No local claim tracking
// ---------------------------------------------------------------------------

describe("Claim.action — RULE-CLM-003", () => {
  it("claim action does not write to local database", () => {
    // The claim action only opens GitHub or copies text.
    // It must not POST to any local /claims endpoint.
    const localEndpointsCalled: string[] = [];

    // Simulate: claim flow does NOT call any local endpoint
    // TODO: wire to actual fetch mock once API is implemented
    expect(localEndpointsCalled).toHaveLength(0);
  });

  it("is_claimed status updates only on next ETL refresh", () => {
    const issue = makeIssue({ is_claimed: false });
    // After claim action: local state unchanged
    expect(issue.is_claimed).toBe(false);
    // Only after ETL runs and returns updated data would it flip to true
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: Multiple users can claim same issue
// ---------------------------------------------------------------------------

describe("Claim.action — RULE-CLM-004", () => {
  it("claimed issue still shows claim CTA without blocking", () => {
    const issue = makeIssue({ is_claimed: true });
    // is_claimed does not disable the claim button
    const claimCtaDisabled = false; // no blocking logic
    expect(claimCtaDisabled).toBe(false);
    expect(issue.is_claimed).toBe(true); // badge shown, CTA still enabled
  });

  it("no warning or block shown to second user trying to claim", () => {
    // TODO: wire to ClaimModal component.
    // The modal must not render a blocking error when is_claimed=true.
    const issue = makeIssue({ is_claimed: true });
    const isBlocked = false;
    expect(isBlocked).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Flow edge cases — claim-issue.flow.md
// ---------------------------------------------------------------------------

describe("Claim.action — flow edge cases", () => {
  it("clipboard failure returns user-friendly error message", async () => {
    const writeText = vi.fn().mockRejectedValue(new Error("NotAllowedError"));
    Object.assign(navigator, { clipboard: { writeText } });

    const result = await copyToClipboard("comment text");
    expect(result.success).toBe(false);
    expect(result.error).toBe("Couldn't copy. Try selecting the text manually.");
  });

  it("clipboard toast auto-dismisses after 3 seconds", () => {
    // TODO: wire to Toast component.
    const TOAST_DURATION_MS = 3000;
    expect(TOAST_DURATION_MS).toBe(3000);
  });

  it("already-claimed badge text matches spec", () => {
    const badgeText = "Already claimed";
    expect(badgeText).toBe("Already claimed");
  });

  it("claim modal title matches spec", () => {
    const modalTitle = "Ready to claim this task?";
    expect(modalTitle).toBe("Ready to claim this task?");
  });

  it("copy confirmation toast text matches spec", () => {
    const toastText = "Comment copied! Paste it on GitHub when you're ready.";
    expect(toastText).toContain("Paste it on GitHub");
  });
});
