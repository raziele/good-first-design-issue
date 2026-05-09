/**
 * Tests for Issue Detail view rules.
 * RULE-ISS-003: Issue detail view shows full information
 * RULE-ISS-004: Claimed issues are marked
 */

import { describe, it, expect, afterEach } from "vitest";
import { render, screen, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { IssueDetail } from "../../src/frontend/src/components/IssueDetail";

const detailIssue = {
  id: "iss-2",
  title: "Onboarding flow redesign",
  description:
    "We need a complete redesign of the onboarding experience. This includes new wireframes, user flow diagrams, and Figma mockups for each step. The current onboarding has a 60% drop-off rate and needs urgent attention from a UX perspective.",
  repo_name: "owner/design-repo",
  repo_stars: 512,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  freshness_days: 2,
  complexity_score: "high",
  attractiveness_rating: 0.95,
  seniority_level: "senior",
  has_media: true,
  github_url: "https://github.com/owner/design-repo/issues/7",
};

describe("IssueDetail — RULE-ISS-003: detail view shows full information", () => {
  it("displays full (non-truncated) description", () => {
    render(<IssueDetail issue={detailIssue} />);
    const desc = screen.getByTestId("issue-full-description");
    expect(desc.textContent).toContain("complete redesign of the onboarding experience");
    expect(desc.textContent!.length).toBeGreaterThan(200);
  });

  it("displays all attribute scores", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/high/i)).toBeTruthy();
    expect(screen.getByText(/senior/i)).toBeTruthy();
    expect(screen.getByTestId("attractiveness-rating")).toBeTruthy();
  });

  it("displays repo star count", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByText(/512/)).toBeTruthy();
  });

  it("provides a direct link to the GitHub issue", () => {
    render(<IssueDetail issue={detailIssue} />);
    const link = screen.getByRole("link", { name: /github/i });
    expect(link.getAttribute("href")).toBe(
      "https://github.com/owner/design-repo/issues/7"
    );
  });

  it("shows media indicator on detail view when has_media is true", () => {
    render(<IssueDetail issue={detailIssue} />);
    expect(screen.getByTestId("media-indicator")).toBeTruthy();
  });

  it("does not embed images or videos — only shows media indicator", () => {
    render(<IssueDetail issue={detailIssue} />);
    // No <img> or <video> element embedded from description content
    const imgs = document.querySelectorAll("img[data-embedded]");
    const videos = document.querySelectorAll("video");
    expect(imgs.length).toBe(0);
    expect(videos.length).toBe(0);
  });
});

describe("IssueDetail — RULE-ISS-004: claimed issues are marked", () => {
  it("shows 'Already claimed' indicator on detail view when is_claimed", () => {
    render(<IssueDetail issue={{ ...detailIssue, is_claimed: true }} />);
    expect(screen.getByText(/already claimed/i)).toBeTruthy();
  });

  it("claim CTA remains enabled even when issue is claimed", () => {
    render(<IssueDetail issue={{ ...detailIssue, is_claimed: true }} />);
    const claimBtn = screen.getByRole("button", { name: /claim this task/i });
    expect(claimBtn).toBeTruthy();
    expect(claimBtn.hasAttribute("disabled")).toBe(false);
  });
});
