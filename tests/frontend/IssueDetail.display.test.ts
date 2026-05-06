/**
 * Tests for Issue Detail view display behavior.
 *
 * Spec: specs/behavior/issues.spec.md
 * Rules: RULE-ISS-003, RULE-ISS-004
 * Glossary: TERM-001 (Issue), TERM-007 (Attractiveness Rating)
 */

import { describe, it, expect } from "vitest";

interface Issue {
  id: string;
  github_url: string;
  repo_name: string;
  repo_stars: number;
  title: string;
  description: string;
  description_truncated: string;
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
    id: "detail-001",
    github_url: "https://github.com/org/repo/issues/42",
    repo_name: "org/repo",
    repo_stars: 3400,
    title: "Accessibility audit for settings flow",
    description: "Full accessibility audit needed. Covers WCAG 2.1 AA conformance, color contrast, keyboard nav.",
    description_truncated: "Full accessibility audit needed.",
    has_media: false,
    freshness_days: 7,
    classification: "relevant",
    is_claimed: false,
    complexity_score: "high",
    attractiveness_rating: 0.9,
    seniority_level: "senior",
    status: "active",
    ...overrides,
  };
}

interface DetailView {
  fullDescription: string;
  complexityScore: string;
  attractivenessRating: number;
  seniorityLevel: string;
  repoStars: number;
  githubUrl: string;
  showMediaIndicator: boolean;
  claimCtaAvailable: boolean;
  claimBadge: string | null;
}

function renderDetail(issue: Issue): DetailView {
  return {
    fullDescription: issue.description,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    repoStars: issue.repo_stars,
    githubUrl: issue.github_url,
    showMediaIndicator: issue.has_media,
    claimCtaAvailable: true, // always available regardless of is_claimed (RULE-ISS-004)
    claimBadge: issue.is_claimed ? "Already claimed" : null,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueDetail.display", () => {
  it("shows the full description (not truncated)", () => {
    const issue = makeIssue();
    const detail = renderDetail(issue);
    expect(detail.fullDescription).toBe(issue.description);
    expect(detail.fullDescription.length).toBeGreaterThan(
      issue.description_truncated.length
    );
  });

  it("shows complexity score", () => {
    const detail = renderDetail(makeIssue({ complexity_score: "high" }));
    expect(["low", "medium", "high"]).toContain(detail.complexityScore);
  });

  it("shows attractiveness rating", () => {
    const detail = renderDetail(makeIssue({ attractiveness_rating: 0.9 }));
    expect(detail.attractivenessRating).toBeGreaterThanOrEqual(0);
    expect(detail.attractivenessRating).toBeLessThanOrEqual(1);
  });

  it("shows seniority level", () => {
    const detail = renderDetail(makeIssue({ seniority_level: "senior" }));
    expect(["junior", "senior"]).toContain(detail.seniorityLevel);
  });

  it("shows repo star count", () => {
    const detail = renderDetail(makeIssue({ repo_stars: 3400 }));
    expect(typeof detail.repoStars).toBe("number");
    expect(detail.repoStars).toBeGreaterThanOrEqual(0);
  });

  it("provides a direct link to the GitHub issue", () => {
    const detail = renderDetail(makeIssue());
    expect(detail.githubUrl).toMatch(/^https:\/\/github\.com\//);
  });

  it("shows media indicator when issue has media", () => {
    const detail = renderDetail(makeIssue({ has_media: true }));
    expect(detail.showMediaIndicator).toBe(true);
  });

  it("does not show media indicator when issue has no media", () => {
    const detail = renderDetail(makeIssue({ has_media: false }));
    expect(detail.showMediaIndicator).toBe(false);
  });

  // RULE-ISS-004: claimed issues
  it("shows 'Already claimed' badge on claimed issue detail", () => {
    const detail = renderDetail(makeIssue({ is_claimed: true }));
    expect(detail.claimBadge).toBe("Already claimed");
  });

  it("claim CTA is still available even on a claimed issue", () => {
    const detail = renderDetail(makeIssue({ is_claimed: true }));
    expect(detail.claimCtaAvailable).toBe(true);
  });

  it("does not show claim badge on unclaimed issue", () => {
    const detail = renderDetail(makeIssue({ is_claimed: false }));
    expect(detail.claimBadge).toBeNull();
  });
});
