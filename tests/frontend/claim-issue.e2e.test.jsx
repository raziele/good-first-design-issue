/**
 * E2E skeleton tests for the Claim Issue flow.
 * UXI Flow: specs/uxi/flows/claim-issue.flow.md
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import IssueDetail from "../../src/frontend/src/components/IssueDetail";

const issue = {
  id: "github_1",
  github_url: "https://github.com/owner/repo/issues/1",
  title: "Mobile onboarding redesign",
  description:
    "Redesign the entire onboarding flow. Create Figma mockups and user journey maps.",
  description_truncated: "Redesign the entire onboarding flow...",
  repo_name: "owner/repo",
  repo_stars: 800,
  freshness_days: 4,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  complexity_score: "medium",
  attractiveness_rating: 0.85,
  seniority_level: "junior",
  has_media: false,
};

// ---------------------------------------------------------------------------
// Claim flow entry — CTA button present on detail view
// ---------------------------------------------------------------------------

describe("Claim Issue flow — entry", () => {
  it("shows 'Claim This Task' CTA on the detail view", () => {
    render(<IssueDetail issue={issue} />);
    expect(screen.getByRole("button", { name: /claim this task/i })).toBeTruthy();
  });

  it("opens claim options modal when 'Claim This Task' is clicked", async () => {
    render(<IssueDetail issue={issue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => {
      expect(screen.getByText(/ready to claim this task\?/i)).toBeTruthy();
    });
  });
});

// ---------------------------------------------------------------------------
// Path A: Go to GitHub
// ---------------------------------------------------------------------------

describe("Claim Issue flow — Path A: Go to GitHub", () => {
  it("Go to GitHub button opens github issue URL (has href with github.com)", async () => {
    render(<IssueDetail issue={issue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByText(/ready to claim this task\?/i));

    const goToGithub = screen.getByRole("link", { name: /go to github/i });
    expect(goToGithub.getAttribute("href")).toContain("github.com");
  });
});

// ---------------------------------------------------------------------------
// Path B: Copy comment
// ---------------------------------------------------------------------------

describe("Claim Issue flow — Path B: Copy comment", () => {
  it("shows clipboard success message after copying", async () => {
    const mockClipboard = { writeText: vi.fn().mockResolvedValue(undefined) };
    Object.defineProperty(navigator, "clipboard", {
      value: mockClipboard,
      configurable: true,
    });

    render(<IssueDetail issue={issue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByText(/ready to claim this task\?/i));

    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      expect(screen.getByText(/comment copied/i)).toBeTruthy();
    });
    vi.restoreAllMocks();
  });
});

// ---------------------------------------------------------------------------
// Already claimed state — RULE-ISS-004 + RULE-CLM-004
// ---------------------------------------------------------------------------

describe("Claim Issue flow — already claimed issue", () => {
  it("shows 'Already claimed' badge on detail view", () => {
    render(<IssueDetail issue={{ ...issue, is_claimed: true }} />);
    expect(screen.getByText(/already claimed/i)).toBeTruthy();
  });

  it("Claim This Task CTA is still enabled on a claimed issue", () => {
    render(<IssueDetail issue={{ ...issue, is_claimed: true }} />);
    const claimBtn = screen.getByRole("button", { name: /claim this task/i });
    expect(claimBtn.disabled).toBeFalsy();
  });
});
