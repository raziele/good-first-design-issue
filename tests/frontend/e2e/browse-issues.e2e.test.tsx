/**
 * E2E flow tests for Browse Issues flow.
 * Flow: browse-issues.flow.md
 * RULE-ISS-001: Only relevant active issues shown
 * RULE-ISS-005: Default sort by freshness
 * RULE-SRC-001: Search matches title/description
 * RULE-SRC-003: Search + filter combined
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { IssueBrowser } from "../../src/frontend/src/pages/IssueBrowser";

const mockIssues = [
  {
    id: "iss-1",
    title: "Mobile onboarding redesign",
    description: "Full UX audit and new wireframes needed for onboarding.",
    repo_name: "owner/mobile-app",
    repo_stars: 200,
    classification: "relevant",
    status: "active",
    is_claimed: false,
    freshness_days: 2,
    complexity_score: "high",
    attractiveness_rating: 0.9,
    seniority_level: "senior",
    has_media: false,
    github_url: "https://github.com/owner/mobile-app/issues/1",
  },
  {
    id: "iss-2",
    title: "Settings page redesign",
    description: "Redesign the settings layout for accessibility compliance.",
    repo_name: "owner/web-app",
    repo_stars: 50,
    classification: "relevant",
    status: "active",
    is_claimed: false,
    freshness_days: 15,
    complexity_score: "medium",
    attractiveness_rating: 0.7,
    seniority_level: "junior",
    has_media: false,
    github_url: "https://github.com/owner/web-app/issues/5",
  },
  {
    id: "iss-3",
    title: "Backend API refactor",
    description: "Refactor the REST API endpoint.",
    repo_name: "owner/api",
    repo_stars: 10,
    classification: "not_relevant",
    status: "active",
    is_claimed: false,
    freshness_days: 1,
    complexity_score: "low",
    attractiveness_rating: 0.1,
    seniority_level: "junior",
    has_media: false,
    github_url: "https://github.com/owner/api/issues/9",
  },
];

describe("Browse Issues Flow — RULE-ISS-001: only relevant active issues shown", () => {
  it("renders only relevant active issues", async () => {
    render(<IssueBrowser issues={mockIssues} />);
    await waitFor(() => {
      expect(screen.getByText("Mobile onboarding redesign")).toBeTruthy();
      expect(screen.getByText("Settings page redesign")).toBeTruthy();
      expect(screen.queryByText("Backend API refactor")).toBeNull();
    });
  });
});

describe("Browse Issues Flow — RULE-ISS-005: default sort by freshness", () => {
  it("renders issues in freshness order (newest first) by default", async () => {
    render(<IssueBrowser issues={mockIssues} />);
    await waitFor(() => {
      const cards = screen.getAllByTestId("issue-card");
      expect(cards[0]).toHaveTextContent("Mobile onboarding redesign");
      expect(cards[1]).toHaveTextContent("Settings page redesign");
    });
  });
});

describe("Browse Issues Flow — loading and empty states", () => {
  it("shows skeleton cards in loading state", () => {
    render(<IssueBrowser issues={[]} isLoading={true} />);
    expect(screen.getAllByTestId("skeleton-card").length).toBeGreaterThan(0);
  });

  it("shows empty state message when no issues exist at all", () => {
    render(<IssueBrowser issues={[]} isLoading={false} />);
    expect(
      screen.getByText(/no design opportunities right now/i)
    ).toBeTruthy();
  });

  it("shows no-results empty state message when search returns nothing", async () => {
    render(<IssueBrowser issues={mockIssues} />);
    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "blockchain" } });
    await waitFor(() => {
      expect(
        screen.getByText(/no matches.*try adjusting/i)
      ).toBeTruthy();
    });
  });

  it("shows error state with retry button on fetch failure", () => {
    render(<IssueBrowser issues={[]} isLoading={false} hasError={true} />);
    expect(screen.getByText(/couldn't load tasks/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: /retry/i })).toBeTruthy();
  });
});

describe("Browse Issues Flow — RULE-SRC-001 + RULE-SRC-003: search and filter", () => {
  it("navigates to issue detail when a card is clicked", async () => {
    const onSelectIssue = vi.fn();
    render(<IssueBrowser issues={mockIssues} onSelectIssue={onSelectIssue} />);
    await waitFor(() => {
      fireEvent.click(screen.getByText("Mobile onboarding redesign"));
      expect(onSelectIssue).toHaveBeenCalledWith(
        expect.objectContaining({ id: "iss-1" })
      );
    });
  });
});
