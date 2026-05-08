/**
 * E2E skeleton tests for the Browse Issues flow.
 * UXI Flow: specs/uxi/flows/browse-issues.flow.md
 *
 * Tests cover: loading state, empty states, error state, issue listing.
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "../../src/frontend/src/App";

// ---------------------------------------------------------------------------
// Flow states from browse-issues.flow.md
// ---------------------------------------------------------------------------

describe("Browse Issues flow — loading state", () => {
  it("shows skeleton cards while fetching", async () => {
    // Simulate a slow API response
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise(() => {})) // never resolves
    );
    render(<App />);
    expect(screen.getByTestId("skeleton-cards")).toBeTruthy();
    vi.unstubAllGlobals();
  });
});

describe("Browse Issues flow — empty state (no issues at all)", () => {
  it("shows 'No design opportunities right now' when API returns empty list", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ issues: [] }) })
      )
    );
    render(<App />);
    await waitFor(() => {
      expect(
        screen.getByText(/no design opportunities right now/i)
      ).toBeTruthy();
    });
    vi.unstubAllGlobals();
  });
});

describe("Browse Issues flow — error state", () => {
  it("shows error message and retry button when API fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("Network error")))
    );
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/couldn't load tasks/i)).toBeTruthy();
      expect(screen.getByRole("button", { name: /retry/i })).toBeTruthy();
    });
    vi.unstubAllGlobals();
  });
});

describe("Browse Issues flow — success state", () => {
  it("shows issue cards when API returns relevant active issues", async () => {
    const mockIssues = [
      {
        id: "github_1",
        title: "Redesign the settings page",
        description: "Create wireframes for settings.",
        description_truncated: "Create wireframes for settings.",
        repo_name: "owner/repo",
        freshness_days: 2,
        classification: "relevant",
        status: "active",
        is_claimed: false,
        complexity_score: "medium",
        attractiveness_rating: 0.8,
        seniority_level: "junior",
        has_media: false,
        github_url: "https://github.com/owner/repo/issues/1",
      },
    ];
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ issues: mockIssues }) })
      )
    );
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/redesign the settings page/i)).toBeTruthy();
    });
    vi.unstubAllGlobals();
  });
});
