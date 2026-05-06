/**
 * Tests for Issue listing sort and filter visibility behavior.
 *
 * Spec: specs/behavior/issues.spec.md
 * Rules: RULE-ISS-001, RULE-ISS-005
 * Glossary: TERM-009 (Freshness), TERM-004 (Relevant Issue)
 */

import { describe, it, expect } from "vitest";

interface Issue {
  id: string;
  classification: "relevant" | "not_relevant";
  status: "active" | "closed" | "archived";
  freshness_days: number;
}

function makeIssue(overrides: Partial<Issue> & { id: string }): Issue {
  return {
    classification: "relevant",
    status: "active",
    freshness_days: 10,
    ...overrides,
  };
}

function getListingIssues(issues: Issue[]): Issue[] {
  return issues
    .filter((i) => i.classification === "relevant" && i.status === "active")
    .sort((a, b) => a.freshness_days - b.freshness_days);
}

// ---------------------------------------------------------------------------
// RULE-ISS-001: Display only relevant active issues
// ---------------------------------------------------------------------------

describe("IssueList.sorting — RULE-ISS-001 visibility filter", () => {
  it("includes relevant+active issues", () => {
    const issues = [makeIssue({ id: "a", classification: "relevant", status: "active" })];
    expect(getListingIssues(issues)).toHaveLength(1);
  });

  it("excludes not_relevant issues", () => {
    const issues = [makeIssue({ id: "b", classification: "not_relevant", status: "active" })];
    expect(getListingIssues(issues)).toHaveLength(0);
  });

  it("excludes archived issues", () => {
    const issues = [makeIssue({ id: "c", classification: "relevant", status: "archived" })];
    expect(getListingIssues(issues)).toHaveLength(0);
  });

  it("mixed set returns only relevant+active", () => {
    const issues = [
      makeIssue({ id: "show",   classification: "relevant",     status: "active"   }),
      makeIssue({ id: "hide1",  classification: "not_relevant",  status: "active"   }),
      makeIssue({ id: "hide2",  classification: "relevant",      status: "archived" }),
    ];
    const listing = getListingIssues(issues);
    expect(listing).toHaveLength(1);
    expect(listing[0].id).toBe("show");
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort is by freshness ascending (newest first)
// ---------------------------------------------------------------------------

describe("IssueList.sorting — RULE-ISS-005 default sort by freshness", () => {
  it("sorts issues by freshness_days ascending", () => {
    const issues = [
      makeIssue({ id: "old",    freshness_days: 30 }),
      makeIssue({ id: "newest", freshness_days: 1  }),
      makeIssue({ id: "mid",    freshness_days: 10 }),
    ];
    const sorted = getListingIssues(issues);
    expect(sorted.map((i) => i.id)).toEqual(["newest", "mid", "old"]);
  });

  it("single issue retains its position", () => {
    const issues = [makeIssue({ id: "solo", freshness_days: 5 })];
    expect(getListingIssues(issues)[0].id).toBe("solo");
  });

  it("ties in freshness preserve stable order", () => {
    const issues = [
      makeIssue({ id: "first",  freshness_days: 5 }),
      makeIssue({ id: "second", freshness_days: 5 }),
    ];
    const sorted = getListingIssues(issues);
    expect(sorted).toHaveLength(2);
  });
});
