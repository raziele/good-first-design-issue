/**
 * Tests for Issue Card display rules.
 * RULE-ISS-002: Issue card displays preview information
 * RULE-ISS-004: Claimed issues are marked
 */

import { describe, it, expect, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { IssueCard } from "../../src/frontend/src/components/IssueCard";

const baseIssue = {
  id: "iss-1",
  title: "Redesign the settings page",
  description:
    "We need a full UX redesign of the settings page including user flows and wireframes in Figma. The current design is outdated and causes confusion for new users navigating the account section.",
  repo_name: "owner/awesome-repo",
  repo_stars: 128,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  freshness_days: 5,
  complexity_score: "medium",
  attractiveness_rating: 0.8,
  seniority_level: "junior",
  has_media: false,
  github_url: "https://github.com/owner/awesome-repo/issues/42",
};

describe("IssueCard — RULE-ISS-002: card shows required elements", () => {
  it("displays repo name", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/owner\/awesome-repo/i)).toBeTruthy();
  });

  it("displays issue title", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText("Redesign the settings page")).toBeTruthy();
  });

  it("displays truncated description (max ~200 chars)", () => {
    render(<IssueCard issue={baseIssue} />);
    const desc = screen.getByTestId("issue-description-preview");
    expect(desc.textContent!.length).toBeLessThanOrEqual(210);
  });

  it("displays complexity score", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/medium/i)).toBeTruthy();
  });

  it("displays seniority level", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByText(/junior/i)).toBeTruthy();
  });

  it("displays freshness indicator", () => {
    render(<IssueCard issue={baseIssue} />);
    expect(screen.getByTestId("freshness-indicator")).toBeTruthy();
  });

  it("shows media indicator icon when has_media is true", () => {
    render(<IssueCard issue={{ ...baseIssue, has_media: true }} />);
    expect(screen.getByTestId("media-indicator")).toBeTruthy();
  });

  it("does not show media indicator icon when has_media is false", () => {
    render(<IssueCard issue={{ ...baseIssue, has_media: false }} />);
    expect(screen.queryByTestId("media-indicator")).toBeNull();
  });
});

describe("IssueCard — RULE-ISS-004: claimed issues are marked", () => {
  it("shows 'Already claimed' badge when is_claimed is true", () => {
    render(<IssueCard issue={{ ...baseIssue, is_claimed: true }} />);
    expect(screen.getByText(/already claimed/i)).toBeTruthy();
  });

  it("does not show claimed badge when is_claimed is false", () => {
    render(<IssueCard issue={{ ...baseIssue, is_claimed: false }} />);
    expect(screen.queryByText(/already claimed/i)).toBeNull();
  });

  it("claim CTA is still present even when issue is claimed", () => {
    render(<IssueCard issue={{ ...baseIssue, is_claimed: true }} />);
    expect(screen.getByRole("button", { name: /claim this task/i })).toBeTruthy();
  });
});
