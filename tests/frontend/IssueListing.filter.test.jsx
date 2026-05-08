/**
 * Tests for RULE-ISS-001: Display only relevant active issues
 * Tests for RULE-ISS-005: Default sort is by freshness
 * Tests for RULE-SRC-001 to RULE-SRC-003: Search and filtering
 */
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import IssueListing from "../../src/frontend/src/components/IssueListing";

const relevantActive = {
  id: "a",
  title: "Mobile onboarding redesign",
  description: "Redesign the onboarding screens for mobile.",
  description_truncated: "Redesign the onboarding screens...",
  repo_name: "owner/repo",
  freshness_days: 3,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  complexity_score: "low",
  attractiveness_rating: 0.7,
  seniority_level: "junior",
  has_media: false,
};

const notRelevant = {
  id: "b",
  title: "Fix API auth endpoint",
  description: "Backend fix for the REST API.",
  description_truncated: "Backend fix for the REST API.",
  repo_name: "owner/repo",
  freshness_days: 1,
  classification: "not_relevant",
  status: "active",
  is_claimed: false,
  complexity_score: "medium",
  attractiveness_rating: 0.3,
  seniority_level: "junior",
  has_media: false,
};

const archived = {
  id: "c",
  title: "Old design task",
  description: "Old wireframes that are now closed.",
  description_truncated: "Old wireframes...",
  repo_name: "owner/repo",
  freshness_days: 80,
  classification: "relevant",
  status: "archived",
  is_claimed: false,
  complexity_score: "low",
  attractiveness_rating: 0.5,
  seniority_level: "junior",
  has_media: false,
};

const staleRelevant = {
  id: "d",
  title: "Mobile app icons design",
  description: "Create icon set for the mobile app.",
  description_truncated: "Create icon set for the mobile app.",
  repo_name: "owner/repo",
  freshness_days: 45,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  complexity_score: "low",
  attractiveness_rating: 0.6,
  seniority_level: "junior",
  has_media: false,
};

// ---------------------------------------------------------------------------
// RULE-ISS-001: Only relevant + active issues displayed
// ---------------------------------------------------------------------------

describe("IssueListing filtering by classification and status", () => {
  it("shows relevant active issues", () => {
    render(<IssueListing issues={[relevantActive]} />);
    expect(screen.getByText(/mobile onboarding redesign/i)).toBeTruthy();
  });

  it("hides not_relevant issues", () => {
    render(<IssueListing issues={[notRelevant]} />);
    expect(screen.queryByText(/fix api auth endpoint/i)).toBeFalsy();
  });

  it("hides archived issues", () => {
    render(<IssueListing issues={[archived]} />);
    expect(screen.queryByText(/old design task/i)).toBeFalsy();
  });

  it("shows empty state when all issues are filtered out", () => {
    render(<IssueListing issues={[notRelevant, archived]} />);
    expect(screen.getByText(/no design opportunities right now/i)).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// RULE-ISS-005: Default sort by freshness (ascending freshness_days)
// ---------------------------------------------------------------------------

describe("IssueListing default sort", () => {
  it("renders newest issue before older issue", () => {
    render(<IssueListing issues={[staleRelevant, relevantActive]} />);
    const cards = screen.getAllByTestId("issue-card");
    // relevantActive (freshness_days=3) should appear before staleRelevant (freshness_days=45)
    const firstTitle = cards[0].textContent;
    expect(firstTitle).toMatch(/mobile onboarding redesign/i);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-001 + RULE-SRC-003: Search and filter in the listing component
// ---------------------------------------------------------------------------

describe("IssueListing search", () => {
  it("shows issues matching search term in title", async () => {
    render(<IssueListing issues={[relevantActive, staleRelevant]} />);
    const searchInput = screen.getByRole("searchbox");
    fireEvent.change(searchInput, { target: { value: "onboarding" } });
    await waitFor(() => {
      expect(screen.getByText(/mobile onboarding redesign/i)).toBeTruthy();
      expect(screen.queryByText(/mobile app icons design/i)).toBeFalsy();
    });
  });

  it("shows empty state message when search returns no results", async () => {
    render(<IssueListing issues={[relevantActive]} />);
    const searchInput = screen.getByRole("searchbox");
    fireEvent.change(searchInput, { target: { value: "blockchain" } });
    await waitFor(() => {
      expect(screen.getByText(/no matches/i)).toBeTruthy();
    });
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

describe("IssueListing freshness filter", () => {
  it("hides stale issues when Last 7 days filter is applied", async () => {
    render(<IssueListing issues={[relevantActive, staleRelevant]} />);
    const filterButton = screen.getByRole("button", { name: /filter/i });
    fireEvent.click(filterButton);
    const last7 = screen.getByText(/last 7 days/i);
    fireEvent.click(last7);
    await waitFor(() => {
      expect(screen.getByText(/mobile onboarding redesign/i)).toBeTruthy();
      expect(screen.queryByText(/mobile app icons design/i)).toBeFalsy();
    });
  });
});
