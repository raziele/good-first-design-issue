/**
 * Unit tests for frontend issue utility functions.
 * Tests helpers for freshness filtering and description truncation
 * that will live in the production utils module.
 *
 * RULE-ISS-002: description_truncated is ~200 chars
 * RULE-ISS-005: default sort by freshness
 * RULE-SRC-002: freshness filter criteria
 * RULE-SRC-003: AND logic for search + filter
 */

import { describe, it, expect } from "vitest";
import {
  truncateDescription,
  sortByFreshness,
  applyFreshnessFilter,
  combineSearchAndFilter,
} from "../../src/frontend/src/utils/issueUtils";

const makeIssue = (id: string, freshnessDays: number, title = "Issue", description = "") => ({
  id,
  title,
  description,
  freshness_days: freshnessDays,
  classification: "relevant" as const,
  status: "active" as const,
});

describe("truncateDescription — RULE-ISS-002", () => {
  it("truncates description longer than 200 chars", () => {
    const long = "x".repeat(500);
    const result = truncateDescription(long);
    expect(result.length).toBeLessThanOrEqual(210);
  });

  it("appends ellipsis when truncated", () => {
    const long = "x".repeat(500);
    const result = truncateDescription(long);
    expect(result).toMatch(/…$|\.\.\.$/);
  });

  it("returns short descriptions unchanged", () => {
    const short = "Short text.";
    expect(truncateDescription(short)).toBe(short);
  });
});

describe("sortByFreshness — RULE-ISS-005", () => {
  it("sorts issues by freshness_days ascending (lowest = most recent first)", () => {
    const issues = [
      makeIssue("old", 30),
      makeIssue("new", 2),
      makeIssue("mid", 10),
    ];
    const sorted = sortByFreshness(issues);
    expect(sorted.map((i) => i.id)).toEqual(["new", "mid", "old"]);
  });

  it("returns single-item array unchanged", () => {
    const issues = [makeIssue("only", 5)];
    expect(sortByFreshness(issues)).toEqual(issues);
  });
});

describe("applyFreshnessFilter — RULE-SRC-002", () => {
  const issues = [
    makeIssue("a", 3),
    makeIssue("b", 20),
    makeIssue("c", 45),
  ];

  it("returns only issues within max_days when filter applied", () => {
    const result = applyFreshnessFilter(issues, 7);
    expect(result.map((i) => i.id)).toEqual(["a"]);
  });

  it("returns all issues when max_days is null (All time)", () => {
    const result = applyFreshnessFilter(issues, null);
    expect(result.length).toBe(3);
  });
});

describe("combineSearchAndFilter — RULE-SRC-003", () => {
  const issues = [
    makeIssue("mobile-new", 3, "Mobile onboarding redesign", "UX audit needed"),
    makeIssue("mobile-old", 45, "Mobile app icons", "Icon redesign"),
    makeIssue("settings", 5, "Settings page", "Layout review"),
  ];

  it("returns issues matching BOTH search AND freshness", () => {
    const result = combineSearchAndFilter(issues, "mobile", 7);
    expect(result.map((i) => i.id)).toEqual(["mobile-new"]);
  });

  it("returns empty when no issues match combined criteria", () => {
    const result = combineSearchAndFilter(issues, "icons", 7);
    expect(result).toEqual([]);
  });

  it("search is case-insensitive", () => {
    const result = combineSearchAndFilter(issues, "MOBILE", 7);
    expect(result.map((i) => i.id)).toContain("mobile-new");
  });
});
