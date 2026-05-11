/**
 * Tests for RULE-SRC-001, RULE-SRC-002, RULE-SRC-003: client-side search + filter logic
 * SUT: src/frontend/src/utils/searchFilter.ts
 */

import { describe, it, expect } from "vitest";
import { applySearchAndFilter } from "../../src/frontend/src/utils/searchFilter";

type Issue = {
  id: string;
  title: string;
  description: string;
  freshness_days: number;
};

function makeIssue(overrides: Partial<Issue> = {}): Issue {
  return {
    id: "1",
    title: "Issue title",
    description: "Issue description",
    freshness_days: 5,
    ...overrides,
  };
}

describe("applySearchAndFilter — RULE-SRC-001", () => {
  it("returns issue when query matches title", () => {
    const issues = [makeIssue({ id: "1", title: "Mobile onboarding redesign" })];
    const result = applySearchAndFilter(issues, { query: "onboarding" });
    expect(result.map((i) => i.id)).toContain("1");
  });

  it("returns issue when query matches description", () => {
    const issues = [makeIssue({ id: "1", description: "accessibility audit needed" })];
    const result = applySearchAndFilter(issues, { query: "accessibility" });
    expect(result.map((i) => i.id)).toContain("1");
  });

  it("returns empty array when no issues match the query", () => {
    const issues = [makeIssue({ title: "Mobile redesign", description: "Some text" })];
    const result = applySearchAndFilter(issues, { query: "blockchain" });
    expect(result).toEqual([]);
  });

  it("search is case-insensitive", () => {
    const issues = [makeIssue({ id: "1", title: "Mobile Onboarding Redesign" })];
    const result = applySearchAndFilter(issues, { query: "ONBOARDING" });
    expect(result.map((i) => i.id)).toContain("1");
  });
});

describe("applySearchAndFilter — RULE-SRC-002 freshness filter", () => {
  it.each([
    ["last_7_days", 7],
    ["last_30_days", 30],
    ["last_90_days", 90],
  ])("filter '%s' keeps issues within %d days", (filter, maxDays) => {
    const issues = [
      makeIssue({ id: "within", freshness_days: maxDays }),
      makeIssue({ id: "outside", freshness_days: maxDays + 1 }),
    ];
    const result = applySearchAndFilter(issues, { freshnessFilter: filter });
    const ids = result.map((i) => i.id);
    expect(ids).toContain("within");
    expect(ids).not.toContain("outside");
  });

  it("all_time filter returns all issues", () => {
    const issues = [
      makeIssue({ id: "1", freshness_days: 5 }),
      makeIssue({ id: "2", freshness_days: 200 }),
    ];
    const result = applySearchAndFilter(issues, { freshnessFilter: "all_time" });
    expect(result).toHaveLength(2);
  });
});

describe("applySearchAndFilter — RULE-SRC-003 combined AND logic", () => {
  it("returns only issues matching both query and freshness filter", () => {
    const issues = [
      makeIssue({ id: "recent_match", title: "Mobile redesign", freshness_days: 3 }),
      makeIssue({ id: "old_match", title: "Mobile app icons", freshness_days: 45 }),
      makeIssue({ id: "recent_no_match", title: "Totally unrelated", freshness_days: 1 }),
    ];
    const result = applySearchAndFilter(issues, {
      query: "mobile",
      freshnessFilter: "last_7_days",
    });
    expect(result.map((i) => i.id)).toEqual(["recent_match"]);
  });
});
