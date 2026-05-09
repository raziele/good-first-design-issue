/**
 * E2E flow tests for Claim Issue flow.
 * Flow: claim-issue.flow.md
 * RULE-CLM-001: Claim action offers two options
 * RULE-CLM-003: No local claim tracking
 * RULE-CLM-004: Multiple users can claim same issue (no blocking)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { IssueDetailPage } from "../../src/frontend/src/pages/IssueDetailPage";

const claimableIssue = {
  id: "iss-10",
  title: "Mobile onboarding redesign",
  description:
    "We need a full UX redesign of the mobile onboarding flow including wireframes and Figma mockups.",
  repo_name: "owner/mobile-app",
  repo_stars: 340,
  classification: "relevant",
  status: "active",
  is_claimed: false,
  freshness_days: 3,
  complexity_score: "high",
  attractiveness_rating: 0.92,
  seniority_level: "senior",
  has_media: false,
  github_url: "https://github.com/owner/mobile-app/issues/10",
};

describe("Claim Issue Flow — RULE-CLM-001: claim modal appears with two options", () => {
  it("renders 'Claim This Task' button on detail view", () => {
    render(<IssueDetailPage issue={claimableIssue} />);
    expect(screen.getByRole("button", { name: /claim this task/i })).toBeTruthy();
  });

  it("shows claim modal with two options after clicking 'Claim This Task'", async () => {
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
      expect(screen.getByRole("button", { name: /copy comment/i })).toBeTruthy();
    });
  });

  it("modal title asks 'Ready to claim this task?'", async () => {
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => {
      expect(screen.getByText(/ready to claim this task/i)).toBeTruthy();
    });
  });

  it("modal shows a preview of the AI-generated claim comment", async () => {
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => {
      const preview = screen.getByTestId("claim-comment-preview");
      expect(preview.textContent!.trim().length).toBeGreaterThan(0);
    });
  });

  it("modal can be dismissed via close/cancel", async () => {
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByRole("button", { name: /go to github/i }));
    fireEvent.click(screen.getByRole("button", { name: /close|cancel/i }));
    await waitFor(() => {
      expect(screen.queryByText(/ready to claim this task/i)).toBeNull();
    });
  });
});

describe("Claim Issue Flow — Path A: Go to GitHub", () => {
  it("opens GitHub issue URL in new tab when 'Go to GitHub' clicked", async () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByRole("button", { name: /go to github/i }));
    fireEvent.click(screen.getByRole("button", { name: /go to github/i }));
    expect(openSpy).toHaveBeenCalledWith(
      expect.stringContaining("github.com/owner/mobile-app/issues/10"),
      "_blank"
    );
    openSpy.mockRestore();
  });
});

describe("Claim Issue Flow — Path B: Copy comment", () => {
  it("copies comment and shows clipboard confirmation toast", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: writeTextMock },
      writable: true,
    });
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByRole("button", { name: /copy comment/i }));
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      expect(screen.getByText(/comment copied|copied/i)).toBeTruthy();
    });
  });
});

describe("Claim Issue Flow — RULE-CLM-003: no local claim tracking", () => {
  it("does not show updated is_claimed state after claim action completes", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: writeTextMock },
      writable: true,
    });
    render(<IssueDetailPage issue={claimableIssue} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => screen.getByRole("button", { name: /copy comment/i }));
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      // After claiming, the badge should NOT appear — claim tracking is not local
      expect(screen.queryByText(/already claimed/i)).toBeNull();
    });
  });
});

describe("Claim Issue Flow — RULE-CLM-004: already-claimed issue shows no blocking", () => {
  it("claim CTA is still present and enabled for a claimed issue", () => {
    render(<IssueDetailPage issue={{ ...claimableIssue, is_claimed: true }} />);
    const btn = screen.getByRole("button", { name: /claim this task/i });
    expect(btn).toBeTruthy();
    expect(btn.hasAttribute("disabled")).toBe(false);
  });

  it("opens claim modal for already-claimed issue without any warning block", async () => {
    render(<IssueDetailPage issue={{ ...claimableIssue, is_claimed: true }} />);
    fireEvent.click(screen.getByRole("button", { name: /claim this task/i }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
    });
  });
});
