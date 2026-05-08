/**
 * Tests for RULE-ISS-002: Issue card displays preview information
 * Tests for RULE-ISS-004: Claimed issues are marked
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import IssueCard from "../../src/frontend/src/components/IssueCard";

const baseIssue = {
  id: "github_1",
  github_url: "https://github.com/owner/repo/issues/1",
  repo_name: "owner/repo",
  repo_stars: 500,
  title: "Redesign the settings page",
  description:
    "We need to create wireframes and Figma mockups for the settings page, covering all user flows including account management and notification preferences.",
  description_truncated:
    "We need to create wireframes and Figma mockups for the settings page, covering all user flows...",
  labels: ["design", "good first issue"],
  has_media: false,
  freshness_days: 3,
  classification: "relevant",
  is_claimed: false,
  complexity_score: "medium",
  attractiveness_rating: 0.8,
  seniority_level: "junior",
  status: "active",
};

// ---------------------------------------------------------------------------
// RULE-ISS-002: Card shows required elements
// ---------------------------------------------------------------------------

describe("IssueCard display", () => {
  it("shows repo name", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/owner\/repo/i)).toBeTruthy();
  });

  it("shows issue title", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/redesign the settings page/i)).toBeTruthy();
  });

  it("shows truncated description not full description", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.queryByText(baseIssue.description)).toBeFalsy();
    expect(screen.getByText(/wireframes and figma mockups/i)).toBeTruthy();
  });

  it("shows complexity score", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/medium/i)).toBeTruthy();
  });

  it("shows seniority level", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/junior/i)).toBeTruthy();
  });

  it("shows freshness indicator", () => {
    render(<IssueCard issue={baseIssue} />);
    // freshness_days = 3, any indication of days/recency is acceptable
    expect(screen.getByText(/3/)).toBeTruthy();
  });

  it("does not show media indicator when has_media is false", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.queryByTestId("media-indicator")).toBeFalsy();
  });

  it("shows media indicator when has_media is true", () => {
    render(<IssueCard issue={{ ...baseIssue, has_media: true }} />);
    expect(screen.getByTestId("media-indicator")).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-004: Claimed issues are marked
// ---------------------------------------------------------------------------

describe("IssueCard claimed state", () => {
  it("shows 'Already claimed' badge when is_claimed is true", () => {
    render(<IssueCard issue={{ ...baseIssue, is_claimed: true }} />);
    expect(screen.getByText(/already claimed/i)).toBeTruthy();
  });

  it("does not show claimed badge when is_claimed is false", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.queryByText(/already claimed/i)).toBeFalsy();
  });
});
