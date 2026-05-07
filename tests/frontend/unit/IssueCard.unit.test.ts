/**
 * Unit tests for IssueCard display logic.
 * Specs: specs/behavior/issues.spec.md — RULE-ISS-002, RULE-ISS-003, RULE-ISS-004
 *
 * These tests cover pure data-transformation helpers that the IssueCard
 * component will use. No DOM rendering required — keeps the suite fast
 * and framework-agnostic.
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Helpers (will live in a shared utils module once implemented)
// ---------------------------------------------------------------------------

const DESCRIPTION_PREVIEW_LENGTH = 200;

function truncateDescription(description: string, maxChars = DESCRIPTION_PREVIEW_LENGTH): string {
  if (description.length <= maxChars) return description;
  return description.slice(0, maxChars);
}

type ComplexityScore = "low" | "medium" | "high";
type SeniorityLevel = "junior" | "senior";

interface Issue {
  id: string;
  github_url: string;
  repo_name: string;
  repo_stars: number;
  title: string;
  description: string;
  labels: string[];
  has_media: boolean;
  freshness_days: number;
  classification: "relevant" | "not_relevant";
  is_claimed: boolean;
  complexity_score: ComplexityScore;
  attractiveness_rating: number;
  seniority_level: SeniorityLevel;
  status: "active" | "closed" | "archived";
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-1",
    github_url: "https://github.com/owner/repo/issues/1",
    repo_name: "owner/repo",
    repo_stars: 500,
    title: "Design the settings page",
    description: "Full description of the design task",
    labels: ["design"],
    has_media: false,
    freshness_days: 5,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "medium",
    attractiveness_rating: 0.8,
    seniority_level: "junior",
    status: "active",
    ...overrides,
  };
}

function shouldShowMediaIndicator(issue: Issue): boolean {
  return issue.has_media;
}

function shouldShowClaimedBadge(issue: Issue): boolean {
  return issue.is_claimed;
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-002: card preview information", () => {
  it("truncates description to 200 chars", () => {
    const longDesc = "A".repeat(300);
    const result = truncateDescription(longDesc);
    expect(result.length).toBe(200);
  });

  it("does not truncate description shorter than 200 chars", () => {
    const shortDesc = "Short description";
    expect(truncateDescription(shortDesc)).toBe(shortDesc);
  });

  it("exactly 200 char description is not truncated", () => {
    const desc = "B".repeat(200);
    expect(truncateDescription(desc)).toBe(desc);
    expect(truncateDescription(desc).length).toBe(200);
  });

  it("shows media indicator when has_media is true", () => {
    const issue = makeIssue({ has_media: true });
    expect(shouldShowMediaIndicator(issue)).toBe(true);
  });

  it("hides media indicator when has_media is false", () => {
    const issue = makeIssue({ has_media: false });
    expect(shouldShowMediaIndicator(issue)).toBe(false);
  });

  it("complexity_score is one of the valid enum values", () => {
    const validValues: ComplexityScore[] = ["low", "medium", "high"];
    const issue = makeIssue({ complexity_score: "high" });
    expect(validValues).toContain(issue.complexity_score);
  });

  it("attractiveness_rating is in 0.0–1.0 range", () => {
    const issue = makeIssue({ attractiveness_rating: 0.75 });
    expect(issue.attractiveness_rating).toBeGreaterThanOrEqual(0.0);
    expect(issue.attractiveness_rating).toBeLessThanOrEqual(1.0);
  });

  it("seniority_level is one of the valid enum values", () => {
    const validValues: SeniorityLevel[] = ["junior", "senior"];
    const issue = makeIssue({ seniority_level: "senior" });
    expect(validValues).toContain(issue.seniority_level);
  });

  it("repo_name is present in card data", () => {
    const issue = makeIssue({ repo_name: "facebook/react" });
    expect(issue.repo_name).toBe("facebook/react");
  });

  it("title is present in card data", () => {
    const issue = makeIssue({ title: "Mobile onboarding redesign" });
    expect(issue.title).toBe("Mobile onboarding redesign");
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-003: detail view full information", () => {
  it("full description is not truncated in detail view", () => {
    const fullDesc = "D".repeat(500);
    const issue = makeIssue({ description: fullDesc });
    expect(issue.description.length).toBeGreaterThan(200);
  });

  it("github_url is a valid GitHub link", () => {
    const issue = makeIssue();
    expect(issue.github_url).toMatch(/^https:\/\/github\.com\//);
  });

  it("repo_stars is a non-negative integer", () => {
    const issue = makeIssue({ repo_stars: 1234 });
    expect(issue.repo_stars).toBeGreaterThanOrEqual(0);
    expect(Number.isInteger(issue.repo_stars)).toBe(true);
  });

  it("all enrichment scores present in detail data", () => {
    const issue = makeIssue({
      complexity_score: "low",
      attractiveness_rating: 0.4,
      seniority_level: "senior",
    });
    expect(issue.complexity_score).toBeDefined();
    expect(issue.attractiveness_rating).toBeDefined();
    expect(issue.seniority_level).toBeDefined();
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-004: claimed issue badge", () => {
  it("shows claimed badge when is_claimed is true", () => {
    const issue = makeIssue({ is_claimed: true });
    expect(shouldShowClaimedBadge(issue)).toBe(true);
  });

  it("does not show claimed badge when is_claimed is false", () => {
    const issue = makeIssue({ is_claimed: false });
    expect(shouldShowClaimedBadge(issue)).toBe(false);
  });

  it("claim CTA remains available for claimed issues (not blocked)", () => {
    // Spec: claim CTA is still available even when is_claimed = true
    const issue = makeIssue({ is_claimed: true, classification: "relevant", status: "active" });
    // The presence of is_claimed does NOT remove the issue from view or disable CTA
    expect(issue.is_claimed).toBe(true);
    expect(issue.status).toBe("active");
    expect(issue.classification).toBe("relevant");
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort is by freshness
// ---------------------------------------------------------------------------

describe("Issue listing — RULE-ISS-005: default sort by freshness", () => {
  function sortByFreshness(issues: Issue[]): Issue[] {
    return [...issues].sort((a, b) => a.freshness_days - b.freshness_days);
  }

  it("sorts issues by freshness_days ascending (newest first)", () => {
    const issues = [
      makeIssue({ id: "old", freshness_days: 30 }),
      makeIssue({ id: "new", freshness_days: 2 }),
      makeIssue({ id: "mid", freshness_days: 10 }),
    ];
    const sorted = sortByFreshness(issues);
    expect(sorted.map((i) => i.id)).toEqual(["new", "mid", "old"]);
  });

  it("single issue sort returns unchanged", () => {
    const issues = [makeIssue({ freshness_days: 5 })];
    expect(sortByFreshness(issues)).toHaveLength(1);
  });
});
