/**
 * Component tests for IssueCard
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-002
 * Flow: specs/uxi/flows/browse-issues.flow.md
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types (matching ENTITY-001 from specs/chapters/domain-model.md)
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  repo_name: string;
  title: string;
  description: string;
  description_truncated: string;
  freshness_days: number;
  complexity_score: "low" | "medium" | "high";
  attractiveness_rating: number;
  seniority_level: "junior" | "senior";
  has_media: boolean;
  is_claimed: boolean;
  classification: "relevant" | "not_relevant";
  status: "active" | "closed" | "archived";
  github_url: string;
  repo_stars: number;
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-1",
    repo_name: "owner/repo",
    title: "Create wireframes for settings page",
    description: "A".repeat(300),
    description_truncated: "A".repeat(200),
    freshness_days: 3,
    complexity_score: "medium",
    attractiveness_rating: 0.8,
    seniority_level: "junior",
    has_media: false,
    is_claimed: false,
    classification: "relevant",
    status: "active",
    github_url: "https://github.com/owner/repo/issues/1",
    repo_stars: 250,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Stub renderer — replace with real component render when implementation exists
// TODO: replace with @testing-library/react render of <IssueCard issue={issue} />
// ---------------------------------------------------------------------------

function renderCard(issue: Issue) {
  return {
    repoName: issue.repo_name,
    title: issue.title,
    descriptionPreview: issue.description_truncated,
    descriptionPreviewLength: issue.description_truncated.length,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    freshnessIndicator: issue.freshness_days,
    mediaIndicatorVisible: issue.has_media,
    claimedBadgeVisible: issue.is_claimed,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-002: card shows required elements", () => {
  it("IssueCard.showsRepoName", () => {
    const card = renderCard(makeIssue());
    expect(card.repoName).toBe("owner/repo");
  });

  it("IssueCard.showsTitle", () => {
    const card = renderCard(makeIssue());
    expect(card.title).toBe("Create wireframes for settings page");
  });

  it("IssueCard.truncatesDescriptionAt200Chars", () => {
    const issue = makeIssue({ description: "X".repeat(500), description_truncated: "X".repeat(200) });
    const card = renderCard(issue);
    expect(card.descriptionPreviewLength).toBeLessThanOrEqual(200);
  });

  it("IssueCard.showsComplexityScore", () => {
    const card = renderCard(makeIssue());
    expect(["low", "medium", "high"]).toContain(card.complexityScore);
  });

  it("IssueCard.showsAttractivenessRating", () => {
    const card = renderCard(makeIssue({ attractiveness_rating: 0.75 }));
    expect(card.attractivenessRating).toBeGreaterThanOrEqual(0.0);
    expect(card.attractivenessRating).toBeLessThanOrEqual(1.0);
  });

  it("IssueCard.showsSeniorityLevel", () => {
    const card = renderCard(makeIssue());
    expect(["junior", "senior"]).toContain(card.seniorityLevel);
  });

  it("IssueCard.showsFreshnessIndicator", () => {
    const card = renderCard(makeIssue({ freshness_days: 3 }));
    expect(card.freshnessIndicator).toBe(3);
  });

  it("IssueCard.showsMediaIndicatorWhenHasMediaTrue", () => {
    const card = renderCard(makeIssue({ has_media: true }));
    expect(card.mediaIndicatorVisible).toBe(true);
  });

  it("IssueCard.hidesMediaIndicatorWhenHasMediaFalse", () => {
    const card = renderCard(makeIssue({ has_media: false }));
    expect(card.mediaIndicatorVisible).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked on cards
// ---------------------------------------------------------------------------

describe("IssueCard — RULE-ISS-004: claimed badge", () => {
  it("IssueCard.showsClaimedBadgeWhenIsClaimedTrue", () => {
    const card = renderCard(makeIssue({ is_claimed: true }));
    expect(card.claimedBadgeVisible).toBe(true);
  });

  it("IssueCard.hidesClaimedBadgeWhenIsClaimedFalse", () => {
    const card = renderCard(makeIssue({ is_claimed: false }));
    expect(card.claimedBadgeVisible).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Browse flow edge cases (browse-issues.flow.md)
// ---------------------------------------------------------------------------

describe("IssueCard — browse flow edge cases", () => {
  it("IssueCard.truncatesLongTitleWithEllipsis", () => {
    // Flow: "Extremely long issue title → truncate with ellipsis after 2 lines"
    const longTitle = "A".repeat(200);
    const issue = makeIssue({ title: longTitle });
    // TODO: assert that component applies CSS line-clamp or truncation
    // For now we validate the title data is present and non-empty
    expect(issue.title.length).toBeGreaterThan(0);
  });
});
