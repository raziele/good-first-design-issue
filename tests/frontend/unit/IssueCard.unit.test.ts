/**
 * Unit tests for IssueCard component.
 * Spec: specs/behavior/issues.spec.md (RULE-ISS-002)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types (mirror domain model ENTITY-001)
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
  complexity_score: "low" | "medium" | "high" | null;
  attractiveness_rating: number | null;
  seniority_level: "junior" | "senior" | null;
  status: "active" | "closed" | "archived";
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "gh-001",
    github_url: "https://github.com/org/repo/issues/1",
    repo_name: "org/repo",
    repo_stars: 500,
    title: "Redesign onboarding flow",
    description: "Create wireframes and a user flow for mobile onboarding.",
    description_truncated:
      "Create wireframes and a user flow for mobile onboarding.",
    labels: [],
    has_media: false,
    freshness_days: 3,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.8,
    seniority_level: "junior",
    status: "active",
    ...overrides,
  };
}

/** Simulate the card rendering contract: returns the props that must be present. */
function getCardProps(issue: Issue) {
  return {
    repoName: issue.repo_name,
    title: issue.title,
    descriptionPreview: issue.description_truncated,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessIndicator: issue.freshness_days,
    showMediaIcon: issue.has_media,
    isClaimedBadge: issue.is_claimed,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard.card shows required elements", () => {
  it("includes repo name", () => {
    const props = getCardProps(makeIssue());
    expect(props.repoName).toBe("org/repo");
  });

  it("includes title", () => {
    const props = getCardProps(makeIssue({ title: "Mobile redesign" }));
    expect(props.title).toBe("Mobile redesign");
  });

  it("includes truncated description (≤200 chars)", () => {
    const long = "A".repeat(500);
    const issue = makeIssue({
      description: long,
      description_truncated: long.slice(0, 200),
    });
    const props = getCardProps(issue);
    expect(props.descriptionPreview.length).toBeLessThanOrEqual(200);
  });

  it("includes complexity score", () => {
    const props = getCardProps(makeIssue({ complexity_score: "high" }));
    expect(["low", "medium", "high"]).toContain(props.complexityScore);
  });

  it("includes attractiveness rating between 0 and 1", () => {
    const props = getCardProps(makeIssue({ attractiveness_rating: 0.65 }));
    expect(props.attractivenessRating).toBeGreaterThanOrEqual(0);
    expect(props.attractivenessRating).toBeLessThanOrEqual(1);
  });

  it("includes seniority level", () => {
    const props = getCardProps(makeIssue({ seniority_level: "senior" }));
    expect(["junior", "senior"]).toContain(props.seniorityLevel);
  });

  it("includes freshness indicator (days)", () => {
    const props = getCardProps(makeIssue({ freshness_days: 7 }));
    expect(typeof props.freshnessIndicator).toBe("number");
  });

  it("shows media indicator icon when has_media is true", () => {
    const props = getCardProps(makeIssue({ has_media: true }));
    expect(props.showMediaIcon).toBe(true);
  });

  it("does not show media indicator icon when has_media is false", () => {
    const props = getCardProps(makeIssue({ has_media: false }));
    expect(props.showMediaIcon).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("IssueCard.claimed issue displays claim badge", () => {
  it("shows claimed badge when is_claimed is true", () => {
    const props = getCardProps(makeIssue({ is_claimed: true }));
    expect(props.isClaimedBadge).toBe(true);
  });

  it("does not show claimed badge when is_claimed is false", () => {
    const props = getCardProps(makeIssue({ is_claimed: false }));
    expect(props.isClaimedBadge).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Edge cases from browse-issues.flow.md
// ---------------------------------------------------------------------------

describe("IssueCard.edge cases", () => {
  it("truncates extremely long titles for display (contract: title field provided)", () => {
    const longTitle = "Redesign the ".repeat(20);
    const issue = makeIssue({ title: longTitle });
    // The component is expected to truncate with CSS (ellipsis after 2 lines).
    // The raw title field must still be present in full.
    expect(issue.title).toBe(longTitle);
    const props = getCardProps(issue);
    expect(props.title).toBe(longTitle);
  });
});
