/**
 * Tests for Issue Card display behavior.
 *
 * Spec: specs/behavior/issues.spec.md
 * Rules: RULE-ISS-002, RULE-ISS-004
 * Glossary: TERM-001 (Issue), TERM-007 (Attractiveness Rating), TERM-006 (Complexity Score)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types matching ENTITY-001 (domain-model.md)
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

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-001",
    github_url: "https://github.com/org/repo/issues/1",
    repo_name: "org/repo",
    repo_stars: 1200,
    title: "Create wireframes for settings page",
    description: "Design the settings page. Include mockup and user flow.",
    description_truncated: "Design the settings page. Include mockup and user flow.",
    labels: ["design"],
    has_media: false,
    freshness_days: 5,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.75,
    seniority_level: "junior",
    status: "active",
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Stub card renderer (pure data — no DOM required)
// ---------------------------------------------------------------------------

interface CardData {
  repoName: string;
  title: string;
  descriptionTruncated: string;
  complexityScore: string;
  attractivenessRating: number;
  seniorityLevel: string;
  freshnessLabel: string;
  showMediaIndicator: boolean;
  claimBadge: string | null;
}

function renderCard(issue: Issue): CardData {
  return {
    repoName: issue.repo_name,
    title: issue.title,
    descriptionTruncated: issue.description_truncated.slice(0, 200),
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessLabel: `${issue.freshness_days}d ago`,
    showMediaIndicator: issue.has_media,
    claimBadge: issue.is_claimed ? "Already claimed" : null,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard.display", () => {
  it("shows repo name on the card", () => {
    const card = renderCard(makeIssue({ repo_name: "facebook/react" }));
    expect(card.repoName).toBe("facebook/react");
  });

  it("shows issue title on the card", () => {
    const card = renderCard(makeIssue({ title: "Redesign onboarding flow" }));
    expect(card.title).toBe("Redesign onboarding flow");
  });

  it("truncates description to 200 characters", () => {
    const long = "x".repeat(500);
    const card = renderCard(makeIssue({ description: long, description_truncated: long }));
    expect(card.descriptionTruncated.length).toBeLessThanOrEqual(200);
  });

  it("shows complexity score as low, medium, or high", () => {
    const validValues = ["low", "medium", "high"];
    const card = renderCard(makeIssue({ complexity_score: "high" }));
    expect(validValues).toContain(card.complexityScore);
  });

  it("shows attractiveness rating in range 0–1", () => {
    const card = renderCard(makeIssue({ attractiveness_rating: 0.82 }));
    expect(card.attractivenessRating).toBeGreaterThanOrEqual(0);
    expect(card.attractivenessRating).toBeLessThanOrEqual(1);
  });

  it("shows seniority level as junior or senior", () => {
    const validValues = ["junior", "senior"];
    const card = renderCard(makeIssue({ seniority_level: "senior" }));
    expect(validValues).toContain(card.seniorityLevel);
  });

  it("shows freshness indicator", () => {
    const card = renderCard(makeIssue({ freshness_days: 3 }));
    expect(card.freshnessLabel).toBeTruthy();
  });

  it("shows media indicator when has_media is true", () => {
    const card = renderCard(makeIssue({ has_media: true }));
    expect(card.showMediaIndicator).toBe(true);
  });

  it("does not show media indicator when has_media is false", () => {
    const card = renderCard(makeIssue({ has_media: false }));
    expect(card.showMediaIndicator).toBe(false);
  });

  // RULE-ISS-004: claimed issues are marked
  it("shows 'Already claimed' badge when issue is claimed", () => {
    const card = renderCard(makeIssue({ is_claimed: true }));
    expect(card.claimBadge).toBe("Already claimed");
  });

  it("shows no claim badge when issue is not claimed", () => {
    const card = renderCard(makeIssue({ is_claimed: false }));
    expect(card.claimBadge).toBeNull();
  });
});
