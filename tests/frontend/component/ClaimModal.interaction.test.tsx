/**
 * Tests for Claim Issue flow component rules.
 * RULE-CLM-001: Claim action offers two options (Go to GitHub / Copy comment)
 * RULE-CLM-002: Claim comment is AI-generated (contextual, not a fixed template)
 * RULE-CLM-004: Multiple users can claim same issue (no blocking)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { ClaimModal } from "../../src/frontend/src/components/ClaimModal";

const mockIssue = {
  id: "iss-3",
  title: "Mobile onboarding redesign",
  description: "We need a full redesign of the mobile onboarding flow.",
  github_url: "https://github.com/owner/repo/issues/3",
  is_claimed: false,
};

describe("ClaimModal — RULE-CLM-001: claim action offers two options", () => {
  it("renders 'Go to GitHub' option", () => {
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
  });

  it("renders 'Copy comment' option", () => {
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeTruthy();
  });

  it("'Go to GitHub' opens the GitHub issue URL in new tab", () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null);
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /go to github/i }));
    expect(openSpy).toHaveBeenCalledWith(
      expect.stringContaining("github.com/owner/repo/issues/3"),
      "_blank"
    );
    openSpy.mockRestore();
  });

  it("'Copy comment' copies the generated comment to clipboard", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: writeTextMock },
      writable: true,
    });
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      expect(writeTextMock).toHaveBeenCalled();
    });
  });

  it("shows confirmation message after copying", async () => {
    const writeTextMock = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: writeTextMock },
      writable: true,
    });
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      expect(
        screen.getByText(/comment copied|copied/i)
      ).toBeTruthy();
    });
  });

  it("shows error fallback when clipboard API is unavailable", async () => {
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn().mockRejectedValue(new Error("denied")) },
      writable: true,
    });
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    await waitFor(() => {
      expect(screen.getByText(/couldn't copy|manually/i)).toBeTruthy();
    });
  });
});

describe("ClaimModal — RULE-CLM-002: claim comment is AI-generated (contextual)", () => {
  it("displays a non-empty claim comment preview in the modal", () => {
    render(<ClaimModal issue={mockIssue} onClose={() => {}} />);
    const preview = screen.getByTestId("claim-comment-preview");
    expect(preview.textContent!.trim().length).toBeGreaterThan(0);
  });
});

describe("ClaimModal — RULE-CLM-004: no blocking for already-claimed issues", () => {
  it("claim options are shown even when issue is already claimed", () => {
    render(
      <ClaimModal issue={{ ...mockIssue, is_claimed: true }} onClose={() => {}} />
    );
    expect(screen.getByRole("button", { name: /go to github/i })).toBeTruthy();
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeTruthy();
  });

  it("no blocking warning or disabled state when issue is claimed", () => {
    render(
      <ClaimModal issue={{ ...mockIssue, is_claimed: true }} onClose={() => {}} />
    );
    const goBtn = screen.getByRole("button", { name: /go to github/i });
    expect(goBtn.hasAttribute("disabled")).toBe(false);
  });
});
