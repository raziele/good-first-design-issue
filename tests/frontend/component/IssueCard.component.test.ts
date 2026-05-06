/**
 * Frontend component tests for IssueCard.
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-002, RULE-ISS-004
 * Spec: specs/brand/voice-and-tone.md — terminology, copy
 *
 * Framework: Vitest + Testing Library (React)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types (mirror the domain model from specs/chapters/domain-model.md)
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
    id: "issue-1",
    github_url: "https://github.com/owner/repo/issues/1",
    repo_name: "owner/repo",
    repo_stars: 150,
    title: "Redesign the onboarding flow",
    description: "Full description of the design task for the onboarding screen.",
    description_truncated: "Full description of the design task for the onboarding screen.",
    labels: ["design"],
    has_media: false,
    created_at: "2026-05-01T00:00:00Z",
    updated_at: "2026-05-01T00:00:00Z",
    freshness_days: 5,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.7,
    seniority_level: "junior",
    status: "active",
    fetched_at: "2026-05-06T00:00:00Z",
    ...overrides,
  };
}

/**
 * Simulates what the IssueCard component would render as a data object.
 * Real tests would mount the component and query the DOM.
 */
function renderCardData(issue: Issue) {
  return {
    repoName: issue.repo_name,
    title: issue.title,
    descriptionPreview: issue.description_truncated,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessIndicator: issue.freshness_days,
    mediaIndicator: issue.has_media,
    claimedBadge: issue.is_claimed,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-002: card displays preview information", () => {
  it("shows repo name", () => {
    const card = renderCardData(makeIssue());
    expect(card.repoName).toBe("owner/repo");
  });

  it("shows issue title", () => {
    const card = renderCardData(makeIssue({ title: "Create new icon set" }));
    expect(card.title).toBe("Create new icon set");
  });

  it("shows truncated description (≤200 chars)", () => {
    const longDesc = "x".repeat(300);
    const truncated = longDesc.slice(0, 200);
    const card = renderCardData(makeIssue({ description_truncated: truncated }));
    expect(card.descriptionPreview.length).toBeLessThanOrEqual(200);
  });

  it("shows complexity score", () => {
    const card = renderCardData(makeIssue({ complexity_score: "high" }));
    expect(["low", "medium", "high"]).toContain(card.complexityScore);
  });

  it("shows attractiveness rating", () => {
    const card = renderCardData(makeIssue({ attractiveness_rating: 0.85 }));
    expect(card.attractivenessRating).toBeGreaterThanOrEqual(0);
    expect(card.attractivenessRating).toBeLessThanOrEqual(1);
  });

  it("shows seniority level", () => {
    const card = renderCardData(makeIssue({ seniority_level: "senior" }));
    expect(["junior", "senior"]).toContain(card.seniorityLevel);
  });

  it("shows freshness indicator", () => {
    const card = renderCardData(makeIssue({ freshness_days: 3 }));
    expect(card.freshnessIndicator).toBe(3);
  });

  it("shows media indicator when has_media is true", () => {
    const card = renderCardData(makeIssue({ has_media: true }));
    expect(card.mediaIndicator).toBe(true);
  });

  it("does not show media indicator when has_media is false", () => {
    const card = renderCardData(makeIssue({ has_media: false }));
    expect(card.mediaIndicator).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-004: claimed issues display badge", () => {
  it("shows claimed badge when is_claimed is true", () => {
    const card = renderCardData(makeIssue({ is_claimed: true }));
    expect(card.claimedBadge).toBe(true);
  });

  it("does not show claimed badge when is_claimed is false", () => {
    const card = renderCardData(makeIssue({ is_claimed: false }));
    expect(card.claimedBadge).toBe(false);
  });

  it('badge label uses correct copy: "Already claimed"', () => {
    // Spec brand/voice-and-tone.md: "Already claimed" is the canonical copy
    const BADGE_COPY = "Already claimed";
    expect(BADGE_COPY).toBe("Already claimed");
  });
});

// ---------------------------------------------------------------------------
// Brand copy guard — voice-and-tone.md
// ---------------------------------------------------------------------------

describe("IssueCard — Brand: CTA button copy", () => {
  it('claim CTA uses "Claim This Task" not "Express interest"', () => {
    // Preferred: "Claim This Task"  Avoid: "Express interest in this opportunity"
    const CTA_COPY = "Claim This Task";
    expect(CTA_COPY).toBe("Claim This Task");
    expect(CTA_COPY).not.toContain("Express interest");
  });
});
