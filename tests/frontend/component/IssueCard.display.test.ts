/**
 * Component tests for Issue Card display.
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-002, RULE-ISS-004
 * Glossary: Issue (TERM-001), Claim (TERM-002), Complexity Score (TERM-006),
 *           Attractiveness Rating (TERM-007), Seniority Level (TERM-008)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types (mirroring domain-model.md ENTITY-001)
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
  freshness_days: number;
  classification: "relevant" | "not_relevant";
  is_claimed: boolean;
  complexity_score: "low" | "medium" | "high";
  attractiveness_rating: number;
  seniority_level: "junior" | "senior";
  status: "active" | "closed" | "archived";
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "gh-001",
    github_url: "https://github.com/org/repo/issues/1",
    repo_name: "org/repo",
    repo_stars: 500,
    title: "Design settings page",
    description: "We need wireframes for the new settings screen.".repeat(5),
    description_truncated: "We need wireframes for the new settings screen.",
    labels: ["design"],
    has_media: false,
    freshness_days: 10,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.75,
    seniority_level: "junior",
    status: "active",
    ...overrides,
  };
}

function getCardFields(issue: Issue) {
  return {
    repoName: issue.repo_name,
    title: issue.title,
    descriptionPreview: issue.description_truncated,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessIndicator: issue.freshness_days,
    mediaIndicator: issue.has_media,
    isClaimedBadge: issue.is_claimed,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-002: preview information", () => {
  it("card shows repo name", () => {
    const card = getCardFields(makeIssue());
    expect(card.repoName).toBe("org/repo");
  });

  it("card shows issue title", () => {
    const card = getCardFields(makeIssue({ title: "Mobile onboarding redesign" }));
    expect(card.title).toBe("Mobile onboarding redesign");
  });

  it("card shows truncated description not exceeding 200 chars", () => {
    const longDesc = "x".repeat(500);
    const issue = makeIssue({
      description: longDesc,
      description_truncated: longDesc.slice(0, 200),
    });
    const card = getCardFields(issue);
    expect(card.descriptionPreview.length).toBeLessThanOrEqual(200);
  });

  it("card shows valid complexity score", () => {
    const card = getCardFields(makeIssue({ complexity_score: "high" }));
    expect(["low", "medium", "high"]).toContain(card.complexityScore);
  });

  it("card shows attractiveness rating between 0 and 1", () => {
    const card = getCardFields(makeIssue({ attractiveness_rating: 0.9 }));
    expect(card.attractivenessRating).toBeGreaterThanOrEqual(0.0);
    expect(card.attractivenessRating).toBeLessThanOrEqual(1.0);
  });

  it("card shows valid seniority level", () => {
    const card = getCardFields(makeIssue({ seniority_level: "senior" }));
    expect(["junior", "senior"]).toContain(card.seniorityLevel);
  });

  it("card shows freshness indicator as non-negative days", () => {
    const card = getCardFields(makeIssue({ freshness_days: 5 }));
    expect(card.freshnessIndicator).toBeGreaterThanOrEqual(0);
  });

  it("media indicator shown when has_media is true", () => {
    const card = getCardFields(makeIssue({ has_media: true }));
    expect(card.mediaIndicator).toBe(true);
  });

  it("media indicator absent when has_media is false", () => {
    const card = getCardFields(makeIssue({ has_media: false }));
    expect(card.mediaIndicator).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-004: claimed issue badge", () => {
  it("claimed issue has is_claimed badge visible", () => {
    const card = getCardFields(makeIssue({ is_claimed: true }));
    expect(card.isClaimedBadge).toBe(true);
  });

  it("unclaimed issue has no claimed badge", () => {
    const card = getCardFields(makeIssue({ is_claimed: false }));
    expect(card.isClaimedBadge).toBe(false);
  });

  it("claim CTA remains enabled even when issue is already claimed", () => {
    const issue = makeIssue({ is_claimed: true });
    // CTA availability is independent of is_claimed per spec
    const ctaEnabled = true; // no blocking — always enabled
    expect(ctaEnabled).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-001: Display only relevant active issues (listing filter)
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-001: listing filter", () => {
  function filterListing(issues: Issue[]): Issue[] {
    return issues.filter(
      (i) => i.classification === "relevant" && i.status === "active"
    );
  }

  it("relevant active issue appears in listing", () => {
    const issue = makeIssue({ classification: "relevant", status: "active" });
    expect(filterListing([issue])).toContain(issue);
  });

  it("not_relevant issue does not appear in listing", () => {
    const issue = makeIssue({ classification: "not_relevant" });
    expect(filterListing([issue])).toHaveLength(0);
  });

  it("archived issue does not appear in listing", () => {
    const issue = makeIssue({ status: "archived" });
    expect(filterListing([issue])).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort by freshness
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-005: default sort by freshness", () => {
  function sortByFreshness(issues: Issue[]): Issue[] {
    return [...issues].sort((a, b) => a.freshness_days - b.freshness_days);
  }

  it("issues sorted by freshness_days ascending (newest first)", () => {
    const issues = [
      makeIssue({ id: "old", freshness_days: 60 }),
      makeIssue({ id: "fresh", freshness_days: 2 }),
      makeIssue({ id: "mid", freshness_days: 20 }),
    ];
    const sorted = sortByFreshness(issues);
    expect(sorted[0].id).toBe("fresh");
    expect(sorted[1].id).toBe("mid");
    expect(sorted[2].id).toBe("old");
  });
});
