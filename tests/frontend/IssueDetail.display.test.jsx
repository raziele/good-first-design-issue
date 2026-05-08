/**
 * Tests for RULE-ISS-003: Issue detail view shows full information
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import IssueDetail from "../../src/frontend/src/components/IssueDetail";

const detailIssue = {
  id: "github_1",
  github_url: "https://github.com/owner/repo/issues/1",
  repo_name: "owner/repo",
  repo_stars: 1200,
  title: "Redesign the settings page",
  description:
    "We need to create comprehensive wireframes and Figma mockups for the settings page. This includes all user flows: account management, notification preferences, privacy settings, and integrations. The designer should provide high-fidelity designs.",
  description_truncated: "We need to create comprehensive wireframes and Figma mockups...",
  labels: ["design"],
  has_media: true,
  freshness_days: 5,
  classification: "relevant",
  is_claimed: false,
  complexity_score: "high",
  attractiveness_rating: 0.9,
  seniority_level: "senior",
  status: "active",
};

// ---------------------------------------------------------------------------
// RULE-ISS-003: Detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueDetail display", () => {
  it("shows full description (not truncated)", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/high-fidelity designs/i)).toBeTruthy();
  });

  it("shows complexity score", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/high/i)).toBeTruthy();
  });

  it("shows attractiveness rating", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/0\.9/)).toBeTruthy();
  });

  it("shows seniority level", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/senior/i)).toBeTruthy();
  });

  it("shows repo star count", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/1200/)).toBeTruthy();
  });

  it("provides direct link to GitHub issue", () => {
    render(<IssueDetail issue={detailIssue} />);
    const link = screen.getByRole("link", { name: /github/i });
    expect(link.getAttribute("href")).toBe(detailIssue.github_url);
  });

  it("shows media indicator when has_media is true", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByTestId("media-indicator")).toBeTruthy();
  });

  it("does not embed images inline — only shows indicator", () => {
    render(<IssueDetail issue={detailIssue} />);
    const images = screen.queryAllByRole("img");
    // No embedded issue images; any <img> present must be the indicator icon only
    const embeddedImages = images.filter((img) =>
      img.getAttribute("src")?.includes("github.com")
    );
    expect(embeddedImages).toHaveLength(0);
  });
});
