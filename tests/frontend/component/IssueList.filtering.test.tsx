/**
 * Tests for RULE-ISS-001: IssueList renders only relevant + active issues.
 * Tests for RULE-ISS-005: IssueList default sort is by freshness.
 * SUT: ../../src/frontend/src/components/IssueList
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import IssueList from "../../src/frontend/src/components/IssueList";

const ISSUES = [
  {
    id: "1",
    classification: "relevant",
    status: "active",
    title: "Design the onboarding flow",
    freshness_days: 5,
    repo_name: "org/project",
    description_truncated: "Short desc",
    complexity_score: "low",
    attractiveness_rating: 0.7,
    seniority_level: "junior",
    has_media: false,
    is_claimed: false,
    github_url: "https://github.com/org/project/issues/1",
  },
  {
    id: "2",
    classification: "not_relevant",
    status: "active",
    title: "Fix backend auth",
    freshness_days: 1,
    repo_name: "org/project",
    description_truncated: "Backend fix",
    complexity_score: "high",
    attractiveness_rating: 0.2,
    seniority_level: "senior",
    has_media: false,
    is_claimed: false,
    github_url: "https://github.com/org/project/issues/2",
  },
  {
    id: "3",
    classification: "relevant",
    status: "archived",
    title: "Old icon redesign",
    freshness_days: 100,
    repo_name: "org/project",
    description_truncated: "Old task",
    complexity_score: "low",
    attractiveness_rating: 0.5,
    seniority_level: "junior",
    has_media: false,
    is_claimed: false,
    github_url: "https://github.com/org/project/issues/3",
  },
  {
    id: "4",
    classification: "relevant",
    status: "active",
    title: "Redesign the dashboard",
    freshness_days: 2,
    repo_name: "org/project",
    description_truncated: "Dashboard task",
    complexity_score: "medium",
    attractiveness_rating: 0.9,
    seniority_level: "senior",
    has_media: false,
    is_claimed: false,
    github_url: "https://github.com/org/project/issues/4",
  },
];

describe("IssueList — filtering (RULE-ISS-001)", () => {
  it("renders relevant active issues", () => {
    render(<IssueList issues={ISSUES} />);
    expect(screen.getByText(/Design the onboarding flow/i)).toBeDefined();
    expect(screen.getByText(/Redesign the dashboard/i)).toBeDefined();
  });

  it("hides not_relevant issues", () => {
    render(<IssueList issues={ISSUES} />);
    expect(screen.queryByText(/Fix backend auth/i)).toBeNull();
  });

  it("hides archived issues from main listing", () => {
    render(<IssueList issues={ISSUES} />);
    expect(screen.queryByText(/Old icon redesign/i)).toBeNull();
  });
});

describe("IssueList — default sort (RULE-ISS-005)", () => {
  it("renders issues with newer freshness_days first", () => {
    render(<IssueList issues={ISSUES} />);
    const titles = screen.getAllByRole("heading", { level: 2 });
    const titleTexts = titles.map((h) => h.textContent ?? "");
    // id="4" freshness_days=2 should appear before id="1" freshness_days=5
    const idx4 = titleTexts.findIndex((t) => /Redesign the dashboard/i.test(t));
    const idx1 = titleTexts.findIndex((t) => /Design the onboarding flow/i.test(t));
    expect(idx4).toBeLessThan(idx1);
  });
});
