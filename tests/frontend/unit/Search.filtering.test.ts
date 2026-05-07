/**
 * Frontend unit tests for Search and Filtering logic.
 * Spec: specs/behavior/search.spec.md — RULE-SRC-001 through RULE-SRC-004
 * Flow: specs/uxi/flows/search.flow.md
 * Glossary: Freshness (TERM-009), Issue (TERM-001)
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Issue {
  id: string;
  title: string;
  description: string;
  freshness_days: number;
}

// ---------------------------------------------------------------------------
// Pure filter/search functions (mirror what the frontend state logic does)
// ---------------------------------------------------------------------------

function fullTextSearch(issues: Issue[], query: string): Issue[] {
  const q = query.toLowerCase();
  return issues.filter(
    (i) =>
      i.title.toLowerCase().includes(q) ||
      i.description.toLowerCase().includes(q)
  );
}

const FRESHNESS_MAP: Record<string, number | null> = {
  "Last 7 days": 7,
  "Last 30 days": 30,
  "Last 90 days": 90,
  "All time": null,
};

function filterByFreshness(issues: Issue[], label: string): Issue[] {
  const maxDays = FRESHNESS_MAP[label];
  if (maxDays === null) return issues;
  return issues.filter((i) => i.freshness_days <= maxDays);
}

function applyFilters(
  issues: Issue[],
  query: string,
  freshnessLabel: string
): Issue[] {
  let result = issues;
  if (query.length >= 2) {
    result = fullTextSearch(result, query);
  }
  result = filterByFreshness(result, freshnessLabel);
  return result;
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------

function makeIssue(
  id: string,
  title: string,
  description: string,
  freshness_days: number
): Issue {
  return { id, title, description, freshness_days };
}

// ---------------------------------------------------------------------------
// RULE-SRC-001: Full-text search
// ---------------------------------------------------------------------------

describe("Search — RULE-SRC-001: full-text search", () => {
  it("search matches title", () => {
    const issues = [makeIssue("1", "Mobile onboarding redesign", "", 5)];
    expect(fullTextSearch(issues, "onboarding")).toHaveLength(1);
  });

  it("search matches description", () => {
    const issues = [makeIssue("1", "Unrelated title", "accessibility audit", 5)];
    expect(fullTextSearch(issues, "accessibility")).toHaveLength(1);
  });

  it("search returns empty when no match", () => {
    const issues = [makeIssue("1", "Design work", "UX improvements", 5)];
    expect(fullTextSearch(issues, "blockchain")).toHaveLength(0);
  });

  it("search is case-insensitive", () => {
    const issues = [makeIssue("1", "Mobile Redesign", "", 5)];
    expect(fullTextSearch(issues, "MOBILE")).toHaveLength(1);
  });

  it("search matches both title and description — includes all matches", () => {
    const issues = [
      makeIssue("a", "Dark mode design", "nothing", 5),
      makeIssue("b", "Unrelated", "dark mode toggle needed", 5),
      makeIssue("c", "Unrelated", "nothing", 5),
    ];
    const results = fullTextSearch(issues, "dark mode");
    const ids = results.map((r) => r.id);
    expect(ids).toContain("a");
    expect(ids).toContain("b");
    expect(ids).not.toContain("c");
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

describe("Search — RULE-SRC-002: freshness filter", () => {
  it("Last 7 days — includes issues within window", () => {
    const issues = [
      makeIssue("fresh", "A", "B", 3),
      makeIssue("old", "C", "D", 20),
    ];
    const result = filterByFreshness(issues, "Last 7 days");
    expect(result.map((r) => r.id)).toContain("fresh");
    expect(result.map((r) => r.id)).not.toContain("old");
  });

  it("Last 30 days — boundary value included", () => {
    const issues = [makeIssue("1", "A", "B", 30)];
    expect(filterByFreshness(issues, "Last 30 days")).toHaveLength(1);
  });

  it("Last 90 days — excludes beyond 90", () => {
    const issues = [
      makeIssue("in", "A", "B", 89),
      makeIssue("out", "C", "D", 91),
    ];
    const result = filterByFreshness(issues, "Last 90 days");
    expect(result.map((r) => r.id)).toContain("in");
    expect(result.map((r) => r.id)).not.toContain("out");
  });

  it("All time — returns everything", () => {
    const issues = [makeIssue("1", "A", "B", 1), makeIssue("2", "C", "D", 365)];
    expect(filterByFreshness(issues, "All time")).toHaveLength(2);
  });

  it("freshness filter options match spec exactly", () => {
    const expectedLabels = ["Last 7 days", "Last 30 days", "Last 90 days", "All time"];
    expect(Object.keys(FRESHNESS_MAP)).toEqual(expectedLabels);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-003: Search and filter combine (AND logic)
// ---------------------------------------------------------------------------

describe("Search — RULE-SRC-003: combined search and filter", () => {
  it("combined search and filter — only matching issue returned", () => {
    const issues = [
      makeIssue("match", "Mobile redesign", "", 3),
      makeIssue("too-old", "Mobile app icons", "", 45),
    ];
    const result = applyFilters(issues, "mobile", "Last 7 days");
    expect(result.map((r) => r.id)).toContain("match");
    expect(result.map((r) => r.id)).not.toContain("too-old");
  });

  it("AND logic yields empty when no intersection", () => {
    const issues = [makeIssue("1", "Dark mode design", "", 40)];
    expect(applyFilters(issues, "dark mode", "Last 7 days")).toHaveLength(0);
  });

  it("filter only — no query returns all time results", () => {
    const issues = [
      makeIssue("1", "Accessibility", "", 200),
      makeIssue("2", "Mobile", "", 1),
    ];
    const result = applyFilters(issues, "", "All time");
    expect(result).toHaveLength(2);
  });
});

// ---------------------------------------------------------------------------
// Flow edge cases: specs/uxi/flows/search.flow.md
// ---------------------------------------------------------------------------

describe("Search flow edge cases", () => {
  it("query shorter than 2 chars does not trigger search", () => {
    const issues = [makeIssue("1", "Design work", "UX", 5)];
    // per flow: < 2 chars → no search executed
    const result = applyFilters(issues, "a", "All time");
    // No query applied → returns all
    expect(result).toHaveLength(1);
  });

  it("special characters in search do not throw — search proceeds", () => {
    const issues = [makeIssue("1", "Design work (v2)", "", 5)];
    expect(() => applyFilters(issues, "(v2)", "All time")).not.toThrow();
  });

  it("empty results when both search and filter return no matches", () => {
    const issues = [makeIssue("1", "Backend work", "", 5)];
    const result = applyFilters(issues, "design", "Last 7 days");
    expect(result).toHaveLength(0);
  });
});
