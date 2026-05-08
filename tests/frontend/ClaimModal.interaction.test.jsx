/**
 * Tests for RULE-CLM-001: Claim action offers two options
 * Tests for RULE-CLM-004: Multiple users can claim same issue (no blocking)
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import ClaimModal from "../../src/frontend/src/components/ClaimModal";

const issue = {
  id: "github_1",
  github_url: "https://github.com/owner/repo/issues/1",
  title: "Redesign the settings page",
  description: "Create wireframes for the settings page.",
  classification: "relevant",
  is_claimed: false,
};

const claimedIssue = {
  ...issue,
  id: "github_2",
  is_claimed: true,
};

// ---------------------------------------------------------------------------
// RULE-CLM-001: Claim action shows two options
// ---------------------------------------------------------------------------

describe("ClaimModal", () => {
  it("shows 'Go to GitHub' option", () => {
    render(<ClaimModal issue={issue} onClose={() => {}} />);
    expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
  });

  it("shows 'Copy comment' option", () => {
    render(<ClaimModal issue={issue} onClose={() => {}} />);
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeTruthy();
  });

  it("shows a preview of the claim comment", () => {
    render(<ClaimModal issue={issue} onClose={() => {}} />);
    expect(screen.getByTestId("claim-comment-preview")).toBeTruthy();
  });

  it("shows modal title 'Ready to claim this task?'", () => {
    render(<ClaimModal issue={issue} onClose={() => {}} />);
    expect(screen.getByText(/ready to claim this task\?/i)).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-001 path B: Copy comment — clipboard confirmation
// ---------------------------------------------------------------------------

describe("ClaimModal copy comment path", () => {
  it("shows confirmation message after copy", async () => {
    const mockClipboard = { writeText: vi.fn().mockResolvedValue(undefined) };
    Object.defineProperty(navigator, "clipboard", {
      value: mockClipboard,
      configurable: true,
    });

    render(<ClaimModal issue={issue} onClose={() => {}} />);
    const copyBtn = screen.getByRole("button", { name: /copy comment/i });
    fireEvent.click(copyBtn);

    await waitFor(() => {
      expect(
        screen.getByText(/comment copied/i)
      ).toBeTruthy();
    });
  });
});

// ---------------------------------------------------------------------------
// RULE-CLM-004: No blocking for already-claimed issues
// ---------------------------------------------------------------------------

describe("ClaimModal with already-claimed issue", () => {
  it("still shows both claim options even when issue is already claimed", () => {
    render(<ClaimModal issue={claimedIssue} onClose={() => {}} />);
    expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeTruthy();
  });

  it("does not show a blocking error or disable claim buttons", () => {
    render(<ClaimModal issue={claimedIssue} onClose={() => {}} />);
    const goBtn = screen.getByRole("button", { name: /go to github/i });
    expect(goBtn.disabled).toBeFalsy();
  });
});
