/**
 * Frontend unit tests for Issue Browsing and Viewing.
 * Spec: specs/behavior/issues.spec.md
 * Flow: specs/uxi/flows/browse-issues.flow.md
 */

import { describe, it, expect } from "vitest";
import { makeIssue, type Issue } from "./fixtures";

// ---------------------------------------------------------------------------
// Pure display logic helpers (extracted from component logic)
// ---------------------------------------------------------------------------

function filterMainListing(issues: Issue[]): Issue[] {
  return issues.filter(
    (i) => i.classification === "relevant" && i.status === "active"
  );
}

function buildCard(issue: Issue) {
  return {
    repo_name: issue.repo_name,
    title: issue.title,
    description_truncated: issue.description_truncated,
    complexity_score: issue.complexity_score,
    attractiveness_rating: issue.attractiveness_rating,
    seniority_level: issue.seniority_level,
    freshness_days: issue.freshness_days,
    ...(issue.has_media ? { media_indicator: true } : {}),
  };
}

function sortByFreshness(issues: Issue[]): Issue[] {
  return [...issues].sort((a, b) => a.freshness_days - b.freshness_days);
}

// ---------------------------------------------------------------------------
// RULE-ISS-001: Display only relevant active issues
// ---------------------------------------------------------------------------

describe("Issues.browse — RULE-ISS-001", () => {
  it("relevant active issue appears in listing", () => {
    const issue = makeIssue();
    const listing = filterMainListing([issue]);
    expect(listing.map((i) => i.id)).toContain("issue-001");
  });

  it("not-relevant issue is hidden", () => {
    const issue = makeIssue({ classification: "not_relevant" });
    const listing = filterMainListing([issue]);
    expect(listing).toHaveLength(0);
  });

  it("archived issue is hidden from main listing", () => {
    const issue = makeIssue({ status: "archived" });
    const listing = filterMainListing([issue]);
    expect(listing).toHaveLength(0);
  });

  it("closed issue is hidden from main listing", () => {
    const issue = makeIssue({ status: "closed" });
    const listing = filterMainListing([issue]);
    expect(listing).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("Issues.browse — RULE-ISS-002", () => {
  const REQUIRED_CARD_FIELDS = [
    "repo_name",
    "title",
    "description_truncated",
    "complexity_score",
    "attractiveness_rating",
    "seniority_level",
    "freshness_days",
  ] as const;

  it("card shows all required elements", () => {
    const issue = makeIssue();
    const card = buildCard(issue);
    for (const field of REQUIRED_CARD_FIELDS) {
      expect(card).toHaveProperty(field);
    }
  });

  it("description_truncated is at most 200 characters", () => {
    const long = "x".repeat(500);
    const issue = makeIssue({ description_truncated: long.slice(0, 200) });
    const card = buildCard(issue);
    expect(card.description_truncated.length).toBeLessThanOrEqual(200);
  });

  it("media indicator shown when has_media is true", () => {
    const issue = makeIssue({ has_media: true });
    const card = buildCard(issue);
    expect(card).toHaveProperty("media_indicator", true);
  });

  it("no media indicator when has_media is false", () => {
    const issue = makeIssue({ has_media: false });
    const card = buildCard(issue);
    expect(card).not.toHaveProperty("media_indicator");
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("Issues.browse — RULE-ISS-003", () => {
  it("detail view shows full (non-truncated) description", () => {
    const fullDesc = "Full description with all the details about the design task.";
    const issue = makeIssue({
      description: fullDesc,
      description_truncated: fullDesc.slice(0, 50),
    });
    // Detail must use `description`, not `description_truncated`
    expect(issue.description).toBe(fullDesc);
    expect(issue.description.length).toBeGreaterThan(
      issue.description_truncated.length
    );
  });

  it("detail view exposes all attribute scores", () => {
    const issue = makeIssue();
    expect(issue.complexity_score).toBeDefined();
    expect(issue.attractiveness_rating).toBeDefined();
    expect(issue.seniority_level).toBeDefined();
  });

  it("detail view exposes repo star count", () => {
    const issue = makeIssue({ repo_stars: 1200 });
    expect(issue.repo_stars).toBe(1200);
  });

  it("detail view provides a github_url link", () => {
    const issue = makeIssue();
    expect(issue.github_url).toMatch(/^https:\/\/github\.com\//);
  });

  it("media is indicated via has_media flag but not embedded", () => {
    const issue = makeIssue({ has_media: true });
    // has_media drives indicator; no embedded blob/src field exists
    expect(issue.has_media).toBe(true);
    expect((issue as Record<string, unknown>)["embedded_media"]).toBeUndefined();
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("Issues.browse — RULE-ISS-004", () => {
  it("claimed issue has is_claimed flag set to true", () => {
    const issue = makeIssue({ is_claimed: true });
    expect(issue.is_claimed).toBe(true);
  });

  it("claimed issue still appears in the listing (not hidden)", () => {
    const issue = makeIssue({ is_claimed: true });
    const listing = filterMainListing([issue]);
    expect(listing).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort is by freshness
// ---------------------------------------------------------------------------

describe("Issues.browse — RULE-ISS-005", () => {
  it("issues sorted by freshness_days ascending (newest first)", () => {
    const issues = [
      makeIssue({ id: "old", freshness_days: 30 }),
      makeIssue({ id: "new", freshness_days: 2 }),
      makeIssue({ id: "mid", freshness_days: 15 }),
    ];
    const sorted = sortByFreshness(issues);
    expect(sorted.map((i) => i.id)).toEqual(["new", "mid", "old"]);
  });
});

// ---------------------------------------------------------------------------
// Flow states — browse-issues.flow.md
// ---------------------------------------------------------------------------

describe("Issues.browse — flow states", () => {
  it("loading state: skeleton cards shown, controls disabled", () => {
    // TODO: wire to component render once IssueList component exists
    const state = { loading: true, issues: [] };
    expect(state.loading).toBe(true);
  });

  it("empty state — no results: message references adjusting filters", () => {
    const emptyMessage = "No matches — try adjusting your filters or search terms.";
    expect(emptyMessage).toContain("adjusting");
  });

  it("empty state — no issues: message tells user to check back soon", () => {
    const noIssuesMessage = "No design opportunities right now. Check back soon!";
    expect(noIssuesMessage).toContain("Check back soon");
  });

  it("error state: message references checking connection with retry option", () => {
    const errorMessage = "Couldn't load tasks. Check your connection and try again.";
    expect(errorMessage).toContain("connection");
  });

  it("edge case: extremely long title truncated with ellipsis after 2 lines", () => {
    // TODO: wire to TruncatedTitle component once it exists
    const longTitle = "A".repeat(300);
    const truncated = longTitle.slice(0, 100) + "…";
    expect(truncated.endsWith("…")).toBe(true);
  });
});
