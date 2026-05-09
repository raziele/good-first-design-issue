/**
 * Tests for RULE-ISS-002: IssueCard renders required elements.
 * Tests for RULE-ISS-004: Claimed issue displays visual indicator.
 * SUT: ../../src/frontend/src/components/IssueCard
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import IssueCard from "../../src/frontend/src/components/IssueCard";

const BASE_ISSUE = {
  id: "1",
  repo_name: "facebook/react",
  title: "Redesign the settings page",
  description: "We need wireframes and Figma files for the settings redesign. The current UI is outdated.",
  description_truncated: "We need wireframes and Figma files for the settings redesign.",
  complexity_score: "medium" as const,
  attractiveness_rating: 0.8,
  seniority_level: "junior" as const,
  freshness_days: 5,
  has_media: false,
  is_claimed: false,
  classification: "relevant" as const,
  status: "active" as const,
  github_url: "https://github.com/facebook/react/issues/1",
};

describe("IssueCard — required elements (RULE-ISS-002)", () => {
  it("displays the repo name", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.getByText(/facebook\/react/i)).toBeDefined();
  });

  it("displays the issue title", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.getByText(/Redesign the settings page/i)).toBeDefined();
  });

  it("displays the truncated description", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.getByText(/We need wireframes and Figma files/i)).toBeDefined();
  });

  it("displays the complexity score", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.getByText(/medium/i)).toBeDefined();
  });

  it("displays the seniority level", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.getByText(/junior/i)).toBeDefined();
  });

  it("displays the freshness indicator", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    // freshness_days = 5 — should show some freshness indicator
    expect(screen.getByText(/5/)).toBeDefined();
  });

  it("does not show media indicator when has_media is false", () => {
    render(<IssueCard issue={BASE_ISSUE} />);
    expect(screen.queryByRole("img", { name: /media/i })).toBeNull();
  });

  it("shows media indicator when has_media is true", () => {
    render(<IssueCard issue={{ ...BASE_ISSUE, has_media: true }} />);
    expect(screen.getByRole("img", { name: /media/i })).toBeDefined();
  });
});

describe("IssueCard — claimed state (RULE-ISS-004)", () => {
  it("displays 'Already claimed' badge when is_claimed is true", () => {
    render(<IssueCard issue={{ ...BASE_ISSUE, is_claimed: true }} />);
    expect(screen.getByText(/already claimed/i)).toBeDefined();
  });

  it("does not display 'Already claimed' badge when is_claimed is false", () => {
    render(<IssueCard issue={{ ...BASE_ISSUE, is_claimed: false }} />);
    expect(screen.queryByText(/already claimed/i)).toBeNull();
  });
});
