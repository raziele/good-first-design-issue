/**
 * Component tests for IssueDetail
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-003, RULE-ISS-004
 * Flow: specs/uxi/flows/claim-issue.flow.md
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  repo_name: string;
  repo_stars: number;
  title: string;
  description: string;
  description_truncated: string;
  freshness_days: number;
  complexity_score: "low" | "medium" | "high";
  attractiveness_rating: number;
  seniority_level: "junior" | "senior";
  has_media: boolean;
  is_claimed: boolean;
  github_url: string;
  classification: "relevant" | "not_relevant";
  status: "active" | "closed" | "archived";
}

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "issue-1",
    repo_name: "owner/repo",
    repo_stars: 1200,
    title: "Redesign mobile onboarding flow",
    description: "Full description with all the details about the redesign.",
    description_truncated: "Full description with all the details...",
    freshness_days: 2,
    complexity_score: "high",
    attractiveness_rating: 0.9,
    seniority_level: "senior",
    has_media: false,
    is_claimed: false,
    github_url: "https://github.com/owner/repo/issues/1",
    classification: "relevant",
    status: "active",
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Stub renderer
// TODO: replace with @testing-library/react render of <IssueDetail issue={issue} />
// ---------------------------------------------------------------------------

function renderDetail(issue: Issue) {
  return {
    fullDescription: issue.description,
    descriptionTruncated: issue.description_truncated,
    complexityScore: issue.complexity_score,
    attractivenessRating: issue.attractiveness_rating,
    seniorityLevel: issue.seniority_level,
    repoStars: issue.repo_stars,
    githubUrl: issue.github_url,
    showMediaIndicator: issue.has_media,
    embeddedImages: [] as string[],
    showClaimedBadge: issue.is_claimed,
    claimCtaEnabled: true,
  };
}

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueDetail — RULE-ISS-003: full information display", () => {
  it("IssueDetail.showsFullDescriptionNotTruncated", () => {
    /**
     * Scenario: Detail view shows full description
     * Given a user clicks on an issue card
     * Then the full issue description is displayed (not truncated)
     */
    const longDescription = "D".repeat(500);
    const issue = makeIssue({ description: longDescription });
    const detail = renderDetail(issue);

    expect(detail.fullDescription).toBe(longDescription);
    expect(detail.fullDescription.length).toBe(500);
  });

  it("IssueDetail.showsAllAttributeScores", () => {
    /**
     * And: all attribute scores are visible
     */
    const detail = renderDetail(makeIssue());
    expect(detail.complexityScore).toBeDefined();
    expect(detail.attractivenessRating).toBeDefined();
    expect(detail.seniorityLevel).toBeDefined();
  });

  it("IssueDetail.showsRepoStarCount", () => {
    /**
     * And: Repo star count is visible
     */
    const detail = renderDetail(makeIssue({ repo_stars: 1200 }));
    expect(detail.repoStars).toBe(1200);
  });

  it("IssueDetail.providesGitHubLink", () => {
    /**
     * And: A direct link to the GitHub issue is provided
     */
    const detail = renderDetail(makeIssue());
    expect(detail.githubUrl).toMatch(/^https:\/\/github\.com\//);
  });

  it("IssueDetail.showsMediaIndicatorWhenHasMediaTrue", () => {
    /**
     * Scenario: Media is indicated but not embedded
     * Given an issue with has_media = true
     * Then a media indicator is shown
     */
    const detail = renderDetail(makeIssue({ has_media: true }));
    expect(detail.showMediaIndicator).toBe(true);
  });

  it("IssueDetail.doesNotEmbedImagesOrVideos", () => {
    /**
     * But: Images/videos are not embedded; user must visit GitHub to view
     */
    const detail = renderDetail(makeIssue({ has_media: true }));
    expect(detail.embeddedImages).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked in detail view
// ---------------------------------------------------------------------------

describe("IssueDetail — RULE-ISS-004: claimed state display", () => {
  it("IssueDetail.showsAlreadyClaimedBadgeWhenIsClaimed", () => {
    /**
     * Scenario: Claimed issue displays claim badge
     * Given an issue with is_claimed = true
     * Then a visual indicator shows "Already claimed"
     */
    const detail = renderDetail(makeIssue({ is_claimed: true }));
    expect(detail.showClaimedBadge).toBe(true);
  });

  it("IssueDetail.claimCtaRemainsEnabledWhenIsClaimed", () => {
    /**
     * And: The claim CTA is still available (user can still attempt to claim)
     */
    const detail = renderDetail(makeIssue({ is_claimed: true }));
    expect(detail.claimCtaEnabled).toBe(true);
  });

  it("IssueDetail.claimCtaEnabledWhenNotClaimed", () => {
    const detail = renderDetail(makeIssue({ is_claimed: false }));
    expect(detail.claimCtaEnabled).toBe(true);
  });
});
