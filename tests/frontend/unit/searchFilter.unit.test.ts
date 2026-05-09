/**
 * Tests for RULE-SRC-001, RULE-SRC-002, RULE-SRC-003: Search and filter utility logic.
 * SUT: ../../src/frontend/src/utils/searchFilter
 */
import { describe, it, expect } from "vitest";
import {
  searchIssues,
  applyFreshnessFilter,
  combineSearchAndFilter,
} from "../../src/frontend/src/utils/searchFilter";

interface Issue {
  id: string;
  title: string;
  description: string;
  freshness_days: number;
}

const SAMPLE_ISSUES: Issue[] = [
  { id: "1", title: "Mobile onboarding redesign", description: "", freshness_days: 3 },
  { id: "2", title: "Some issue", description: "accessibility audit for forms", freshness_days: 20 },
  { id: "3", title: "Icon set update", description: "design system tokens", freshness_days: 60 },
  { id: "4", title: "Old design task", description: "", freshness_days: 180 },
];

describe("searchIssues (RULE-SRC-001)", () => {
  it("matches on issue title", () => {
    const result = searchIssues(SAMPLE_ISSUES, "onboarding");
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("1");
  });

  it("matches on issue description", () => {
    const result = searchIssues(SAMPLE_ISSUES, "accessibility");
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("2");
  });

  it("returns empty array when no match", () => {
    const result = searchIssues(SAMPLE_ISSUES, "blockchain");
    expect(result).toHaveLength(0);
  });

  it("is case-insensitive", () => {
    const result = searchIssues(SAMPLE_ISSUES, "ONBOARDING");
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("1");
  });
});

describe("applyFreshnessFilter (RULE-SRC-002)", () => {
  it("filters to Last 7 days (freshness_days <= 7)", () => {
    const result = applyFreshnessFilter(SAMPLE_ISSUES, 7);
    expect(result.map((i: Issue) => i.id)).toEqual(["1"]);
  });

  it("filters to Last 30 days (freshness_days <= 30)", () => {
    const result = applyFreshnessFilter(SAMPLE_ISSUES, 30);
    expect(result.map((i: Issue) => i.id).sort()).toEqual(["1", "2"].sort());
  });

  it("filters to Last 90 days (freshness_days <= 90)", () => {
    const result = applyFreshnessFilter(SAMPLE_ISSUES, 90);
    expect(result.map((i: Issue) => i.id).sort()).toEqual(["1", "2", "3"].sort());
  });

  it("returns all issues when max_days is null (All time)", () => {
    const result = applyFreshnessFilter(SAMPLE_ISSUES, null);
    expect(result).toHaveLength(SAMPLE_ISSUES.length);
  });
});

describe("combineSearchAndFilter (RULE-SRC-003)", () => {
  it("combines search and freshness filter with AND logic", () => {
    const issues: Issue[] = [
      { id: "a", title: "Mobile redesign", description: "", freshness_days: 3 },
      { id: "b", title: "Mobile app icons", description: "", freshness_days: 45 },
    ];
    const result = combineSearchAndFilter(issues, "mobile", 7);
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe("a");
  });

  it("returns empty when search term not found", () => {
    const result = combineSearchAndFilter(SAMPLE_ISSUES, "blockchain", 90);
    expect(result).toHaveLength(0);
  });

  it("returns empty when issue too old despite search match", () => {
    const issues: Issue[] = [
      { id: "a", title: "Mobile app icons", description: "", freshness_days: 45 },
    ];
    const result = combineSearchAndFilter(issues, "mobile", 7);
    expect(result).toHaveLength(0);
  });
});
