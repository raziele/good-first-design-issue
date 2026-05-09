/**
 * E2E flow tests for: Claim Issue (claim-issue.flow.md)
 * Covers: RULE-CLM-001, RULE-CLM-002, RULE-CLM-003, RULE-CLM-004, RULE-ISS-004
 * SUT: ../../src/frontend/src/App
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "../../src/frontend/src/App";

vi.mock("../../src/frontend/src/api/issues", () => ({
  fetchIssues: vi.fn().mockResolvedValue([
    {
      id: "10",
      classification: "relevant",
      status: "active",
      title: "Mobile onboarding redesign",
      description:
        "We need to redesign the onboarding flow for new mobile users.",
      description_truncated: "We need to redesign the onboarding flow.",
      freshness_days: 4,
      complexity_score: "low",
      attractiveness_rating: 0.85,
      seniority_level: "junior",
      has_media: false,
      is_claimed: false,
      repo_name: "org/app",
      github_url: "https://github.com/org/app/issues/10",
    },
    {
      id: "11",
      classification: "relevant",
      status: "active",
      title: "Dashboard UI refresh",
      description: "Refresh the dashboard layout and component styles.",
      description_truncated: "Refresh the dashboard layout.",
      freshness_days: 8,
      complexity_score: "medium",
      attractiveness_rating: 0.75,
      seniority_level: "senior",
      has_media: false,
      is_claimed: true,
      repo_name: "org/app",
      github_url: "https://github.com/org/app/issues/11",
    },
  ]),
}));

vi.mock("../../src/frontend/src/api/claim", () => ({
  generateClaimComment: vi.fn().mockResolvedValue(
    "Hey! I'd love to take this on. I'll work on the onboarding flow."
  ),
}));

describe("Claim Issue flow (claim-issue.flow.md)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    });
  });

  it("opens claim modal when user clicks 'Claim This Task' (RULE-CLM-001)", async () => {
    render(<App />);
    const card = await screen.findByText(/Mobile onboarding redesign/i);
    fireEvent.click(card);
    const claimBtn = await screen.findByRole("button", { name: /claim this task/i });
    fireEvent.click(claimBtn);
    await screen.findByText(/ready to claim this task/i);
  });

  it("modal shows 'Go to GitHub' and 'Copy comment' options (RULE-CLM-001)", async () => {
    render(<App />);
    const card = await screen.findByText(/Mobile onboarding redesign/i);
    fireEvent.click(card);
    const claimBtn = await screen.findByRole("button", { name: /claim this task/i });
    fireEvent.click(claimBtn);
    await screen.findByRole("link", { name: /go to github/i });
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeDefined();
  });

  it("copy comment shows confirmation toast (RULE-CLM-001)", async () => {
    render(<App />);
    const card = await screen.findByText(/Mobile onboarding redesign/i);
    fireEvent.click(card);
    const claimBtn = await screen.findByRole("button", { name: /claim this task/i });
    fireEvent.click(claimBtn);
    await screen.findByRole("button", { name: /copy comment/i });
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await screen.findByText(/comment copied/i);
  });

  it("claimed issue shows 'Already claimed' badge on the card (RULE-ISS-004)", async () => {
    render(<App />);
    await screen.findByText(/Dashboard UI refresh/i);
    expect(screen.getByText(/already claimed/i)).toBeDefined();
  });

  it("claim CTA still available on claimed issue — no block (RULE-CLM-004)", async () => {
    render(<App />);
    const card = await screen.findByText(/Dashboard UI refresh/i);
    fireEvent.click(card);
    const claimBtn = await screen.findByRole("button", { name: /claim this task/i });
    expect(claimBtn).toBeDefined();
    // No warning/block dialog should replace the CTA
    expect(screen.queryByText(/blocked|unavailable/i)).toBeNull();
  });
});
