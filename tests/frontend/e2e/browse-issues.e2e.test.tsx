/**
 * E2E flow tests for: Browse Issues (browse-issues.flow.md)
 * Covers: RULE-ISS-001, RULE-ISS-005, RULE-SRC-001, RULE-SRC-002, RULE-SRC-003
 * SUT: ../../src/frontend/src/App
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "../../src/frontend/src/App";

// Stub the API layer so tests are hermetic
vi.mock("../../src/frontend/src/api/issues", () => ({
  fetchIssues: vi.fn().mockResolvedValue([
    {
      id: "1",
      classification: "relevant",
      status: "active",
      title: "Mobile onboarding redesign",
      description: "Redesign the onboarding flow for mobile users.",
      description_truncated: "Redesign the onboarding flow for mobile users.",
      freshness_days: 3,
      complexity_score: "low",
      attractiveness_rating: 0.9,
      seniority_level: "junior",
      has_media: false,
      is_claimed: false,
      repo_name: "org/app",
      github_url: "https://github.com/org/app/issues/1",
    },
    {
      id: "2",
      classification: "relevant",
      status: "active",
      title: "Icon system overhaul",
      description: "Audit and refresh the icon system for the design library.",
      description_truncated: "Audit and refresh the icon system.",
      freshness_days: 45,
      complexity_score: "medium",
      attractiveness_rating: 0.7,
      seniority_level: "senior",
      has_media: false,
      is_claimed: false,
      repo_name: "org/design",
      github_url: "https://github.com/org/design/issues/2",
    },
    {
      id: "3",
      classification: "not_relevant",
      status: "active",
      title: "Fix database migration",
      description: "Run the pending DB migration scripts.",
      description_truncated: "Run the pending DB migration scripts.",
      freshness_days: 1,
      complexity_score: "high",
      attractiveness_rating: 0.1,
      seniority_level: "senior",
      has_media: false,
      is_claimed: false,
      repo_name: "org/backend",
      github_url: "https://github.com/org/backend/issues/3",
    },
  ]),
}));

describe("Browse Issues flow (browse-issues.flow.md)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows only relevant active issues on load (RULE-ISS-001)", async () => {
    render(<App />);
    await screen.findByText(/Mobile onboarding redesign/i);
    expect(screen.queryByText(/Fix database migration/i)).toBeNull();
  });

  it("sorts issues by freshness — newest first (RULE-ISS-005)", async () => {
    render(<App />);
    await screen.findByText(/Mobile onboarding redesign/i);
    const headings = screen.getAllByRole("heading", { level: 2 });
    const texts = headings.map((h) => h.textContent ?? "");
    const mobileIdx = texts.findIndex((t) => /Mobile onboarding/i.test(t));
    const iconIdx = texts.findIndex((t) => /Icon system/i.test(t));
    expect(mobileIdx).toBeLessThan(iconIdx);
  });

  it("filters issues by search query (RULE-SRC-001)", async () => {
    render(<App />);
    await screen.findByText(/Mobile onboarding redesign/i);
    const searchInput = screen.getByRole("textbox");
    fireEvent.change(searchInput, { target: { value: "icon" } });
    await waitFor(() => {
      expect(screen.queryByText(/Mobile onboarding redesign/i)).toBeNull();
    });
    expect(screen.getByText(/Icon system overhaul/i)).toBeDefined();
  });

  it("applies freshness filter (RULE-SRC-002)", async () => {
    render(<App />);
    await screen.findByText(/Icon system overhaul/i);
    fireEvent.click(screen.getByText(/Last 7 days/i));
    await waitFor(() => {
      expect(screen.queryByText(/Icon system overhaul/i)).toBeNull();
    });
    expect(screen.getByText(/Mobile onboarding redesign/i)).toBeDefined();
  });

  it("combines search + freshness filter (RULE-SRC-003)", async () => {
    render(<App />);
    await screen.findByText(/Mobile onboarding redesign/i);
    const searchInput = screen.getByRole("textbox");
    fireEvent.change(searchInput, { target: { value: "mobile" } });
    fireEvent.click(screen.getByText(/Last 7 days/i));
    await waitFor(() => {
      expect(screen.getByText(/Mobile onboarding redesign/i)).toBeDefined();
      expect(screen.queryByText(/Icon system overhaul/i)).toBeNull();
    });
  });

  it("shows empty state message when no results match (RULE-SRC-001)", async () => {
    render(<App />);
    await screen.findByText(/Mobile onboarding redesign/i);
    const searchInput = screen.getByRole("textbox");
    fireEvent.change(searchInput, { target: { value: "blockchain" } });
    await waitFor(() => {
      expect(
        screen.getByText(/No matches — try adjusting your search terms/i)
      ).toBeDefined();
    });
  });
});
