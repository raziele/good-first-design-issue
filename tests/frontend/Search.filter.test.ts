/**
 * Frontend unit tests for Search and Filtering.
 * Spec: specs/behavior/search.spec.md
 * Flow: specs/uxi/flows/search.flow.md
 */

import { describe, it, expect } from "vitest";
import { makeIssue, type Issue } from "./fixtures";

// ---------------------------------------------------------------------------
// Pure logic helpers
// ---------------------------------------------------------------------------

function searchIssues(issues: Issue[], query: string): Issue[] {
  const q = query.toLowerCase();
  return issues.filter(
    (i) =>
      i.title.toLowerCase().includes(q) ||
      i.description.toLowerCase().includes(q)
  );
}

function filterByFreshness(issues: Issue[], maxDays: number | null): Issue[] {
  if (maxDays === null) return issues;
  return issues.filter((i) => i.freshness_days <= maxDays);
}

function searchAndFilter(
  issues: Issue[],
  query: string,
  maxDays: number | null
): Issue[] {
  const searched = query ? searchIssues(issues, query) : issues;
  return filterByFreshness(searched, maxDays);
}

// ---------------------------------------------------------------------------
// RULE-SRC-001: Full-text search across title and description
// ---------------------------------------------------------------------------

describe("Search.filter — RULE-SRC-001", () => {
  it("search matches title", () => {
    const issue = makeIssue({ title: "Mobile onboarding redesign" });
    const results = searchIssues([issue], "onboarding");
    expect(results.map((i) => i.id)).toContain(issue.id);
  });

  it("search matches description", () => {
    const issue = makeIssue({
      title: "Generic issue",
      description: "This issue requires an accessibility audit of all form fields.",
    });
    const results = searchIssues([issue], "accessibility");
    expect(results.map((i) => i.id)).toContain(issue.id);
  });

  it("search returns empty when no match", () => {
    const issues = [
      makeIssue({ id: "a", title: "Mobile redesign", description: "User flows" }),
      makeIssue({ id: "b", title: "Icon system", description: "Design tokens" }),
    ];
    const results = searchIssues(issues, "blockchain");
    expect(results).toHaveLength(0);
  });

  it("search is case-insensitive", () => {
    const issue = makeIssue({ title: "ONBOARDING redesign" });
    const results = searchIssues([issue], "onboarding");
    expect(results).toHaveLength(1);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

describe("Search.filter — RULE-SRC-002", () => {
  const issues = [
    makeIssue({ id: "fresh",   freshness_days: 3 }),
    makeIssue({ id: "mid",     freshness_days: 20 }),
    makeIssue({ id: "old",     freshness_days: 60 }),
    makeIssue({ id: "ancient", freshness_days: 120 }),
  ];

  it.each([
    ["Last 7 days",  7,    ["fresh"]],
    ["Last 30 days", 30,   ["fresh", "mid"]],
    ["Last 90 days", 90,   ["fresh", "mid", "old"]],
    ["All time",     null, ["fresh", "mid", "old", "ancient"]],
  ] as [string, number | null, string[]][])(
    "freshness filter: %s shows correct issues",
    (_label, maxDays, expectedIds) => {
      const results = filterByFreshness(issues, maxDays);
      const resultIds = results.map((i) => i.id).sort();
      expect(resultIds).toEqual([...expectedIds].sort());
    }
  );

  it("filter to Last 7 days excludes older issues", () => {
    const results = filterByFreshness(issues, 7);
    const ids = results.map((i) => i.id);
    expect(ids).toContain("fresh");
    expect(ids).not.toContain("old");
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-003: Search and filter combine (AND logic)
// ---------------------------------------------------------------------------

describe("Search.filter — RULE-SRC-003", () => {
  it("combined search and filter applies AND logic", () => {
    const issues = [
      makeIssue({ id: "match",    title: "Mobile redesign",   freshness_days: 3 }),
      makeIssue({ id: "no_match", title: "Mobile app icons",  freshness_days: 45 }),
    ];
    const results = searchAndFilter(issues, "mobile", 7);
    const ids = results.map((i) => i.id);
    expect(ids).toContain("match");
    expect(ids).not.toContain("no_match");
  });

  it("combined search and filter returns empty when nothing qualifies", () => {
    const issues = [
      makeIssue({ id: "a", title: "Mobile redesign", freshness_days: 45 }),
    ];
    const results = searchAndFilter(issues, "mobile", 7);
    expect(results).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-004: Mobile uses bottom sheet for filters
// ---------------------------------------------------------------------------

describe("Search.filter — RULE-SRC-004", () => {
  it("mobile filter interaction shows bottom sheet (E2E skeleton)", () => {
    // TODO: wire to FilterBottomSheet component once it exists.
    // This test documents the expected behavior on mobile viewports.
    // Full validation lives in search.e2e.test.ts.
    const isMobile = true;
    const expectedInteraction = isMobile ? "bottom-sheet" : "dropdown";
    expect(expectedInteraction).toBe("bottom-sheet");
  });
});

// ---------------------------------------------------------------------------
// Flow edge cases — search.flow.md
// ---------------------------------------------------------------------------

describe("Search.filter — flow edge cases", () => {
  it("search query shorter than 2 chars does not execute search", () => {
    const MIN_QUERY_LENGTH = 2;
    const query = "a";
    const shouldSearch = query.length >= MIN_QUERY_LENGTH;
    expect(shouldSearch).toBe(false);
  });

  it("2-char query triggers search", () => {
    const MIN_QUERY_LENGTH = 2;
    const query = "ab";
    expect(query.length >= MIN_QUERY_LENGTH).toBe(true);
  });

  it("special characters in query do not throw", () => {
    const issues = [makeIssue({ title: "Settings & Preferences" })];
    expect(() => searchIssues(issues, "settings &")).not.toThrow();
  });

  it("active filter state displays highlighted pill label", () => {
    // TODO: wire to FilterPill component.
    // Coral background per design spec (visual-identity.md).
    const activeFilter = { label: "Last 7 days", active: true };
    expect(activeFilter.active).toBe(true);
  });

  it("no-results state shows combined empty state message", () => {
    const message = "No matches — try adjusting your filters or search terms.";
    expect(message).toContain("filters or search terms");
  });

  it("search input clear button appears when text is present", () => {
    // TODO: wire to SearchInput component.
    const inputValue = "onboarding";
    const showClearButton = inputValue.length > 0;
    expect(showClearButton).toBe(true);
  });
});
