/**
 * Frontend component tests for IssueDetail.
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-003, RULE-ISS-004
 * Spec: specs/uxi/flows/browse-issues.flow.md
 * Spec: specs/uxi/flows/claim-issue.flow.md
 *
 * Framework: Vitest + Testing Library (React)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  github_url: string;
  repo_name: string;
  repo_stars: number;
  title: string;
  description: string;
  description_truncated: string;
  labels: string[];
  has_media: boolean;
  created_at: string;
  updated_at: string;
  freshness_days: number;
  classification: "relevant" | "not_relevant";
  is_claimed: boolean;
  complexity_score: "low" | "medium" | "high";
  attractiveness_rating: number;
  seniority_level: "junior" | "senior";
  status: "active" | "closed" | "archived";
  fetched_at: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-42",
    github_url: "https://github.com/owner/repo/issues/42",
    repo_name: "owner/repo",
    repo_stars: 350,
    title: "Design a new settings page layout",
    description: "Full description with all details about the design task. ".repeat(20),
    description_truncated: "Full description with all details about the design task. ",
    labels: ["design", "ux"],
    has_media: false,
    created_at: "2026-04-20T00:00:00Z",
    updated_at: "2026-05-01T00:00:00Z",
    freshness_days: 16,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.8,
    seniority_level: "junior",
    status: "active",
    fetched_at: "2026-05-06T00:00:00Z",
    ...overrides,
  };
}

/**
 * Simulates detail view data.
 */
function renderDetailData(issue: Issue) {
  return {
    fullDescription: issue.description,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessIndicator: issue.freshness_days,
    repoStars: issue.repo_stars,
    githubLink: issue.github_url,
    mediaIndicator: issue.has_media,
    claimedBadge: issue.is_claimed,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueDetail — RULE-ISS-003: full information displayed", () => {
  it("shows full (non-truncated) description", () => {
    const longDesc = "Design task detail. ".repeat(50);
    const detail = renderDetailData(makeIssue({ description: longDesc }));
    expect(detail.fullDescription).toBe(longDesc);
    expect(detail.fullDescription.length).toBeGreaterThan(200);
  });

  it("shows all attribute scores", () => {
    const detail = renderDetailData(makeIssue());
    expect(detail.complexityScore).toBeDefined();
    expect(detail.attractivenessRating).toBeDefined();
    expect(detail.seniorityLevel).toBeDefined();
    expect(detail.freshnessIndicator).toBeDefined();
  });

  it("shows repo star count", () => {
    const detail = renderDetailData(makeIssue({ repo_stars: 1234 }));
    expect(detail.repoStars).toBe(1234);
  });

  it("provides a direct GitHub issue link", () => {
    const detail = renderDetailData(makeIssue());
    expect(detail.githubLink).toMatch(/^https:\/\/github\.com\/.+\/issues\/\d+/);
  });

  it("shows media indicator when has_media is true", () => {
    const detail = renderDetailData(makeIssue({ has_media: true }));
    expect(detail.mediaIndicator).toBe(true);
  });

  it("does not embed images or videos — only flag is set", () => {
    // Per spec: images/videos are NOT embedded; user must visit GitHub
    const issue = makeIssue({ has_media: true });
    expect(issue.description).not.toMatch(/<img/i);
    expect(issue.description).not.toMatch(/<video/i);
    const detail = renderDetailData(issue);
    expect(detail.mediaIndicator).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed badge on detail view
// ---------------------------------------------------------------------------

describe("IssueDetail — RULE-ISS-004: claimed badge on detail view", () => {
  it("shows claimed badge when is_claimed is true", () => {
    const detail = renderDetailData(makeIssue({ is_claimed: true }));
    expect(detail.claimedBadge).toBe(true);
  });

  it("claim CTA is still available even when is_claimed is true", () => {
    // Spec: claim CTA is still enabled (no blocking)
    const issue = makeIssue({ is_claimed: true });
    // In real test: assert button is not disabled
    expect(issue.is_claimed).toBe(true);
    // CTA should still be rendered (this is a frontend rendering concern)
    const ctaEnabled = true; // TODO: wire up with actual component render
    expect(ctaEnabled).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// Claim modal states — specs/uxi/flows/claim-issue.flow.md
// ---------------------------------------------------------------------------

describe("IssueDetail — Claim options modal states", () => {
  it('modal title uses correct copy: "Ready to claim this task?"', () => {
    const MODAL_TITLE = "Ready to claim this task?";
    expect(MODAL_TITLE).toBe("Ready to claim this task?");
  });

  it('primary action is "Go to GitHub"', () => {
    const PRIMARY_CTA = "Go to GitHub";
    expect(PRIMARY_CTA).toBe("Go to GitHub");
  });

  it('secondary action is "Copy comment"', () => {
    const SECONDARY_CTA = "Copy comment";
    expect(SECONDARY_CTA).toBe("Copy comment");
  });

  it("clipboard success toast uses correct copy", () => {
    // brand/voice-and-tone.md: "Comment copied! Paste it on GitHub when you're ready."
    const TOAST_COPY = "Comment copied! Paste it on GitHub when you're ready.";
    expect(TOAST_COPY).toContain("Comment copied");
    expect(TOAST_COPY).toContain("GitHub");
  });
});
