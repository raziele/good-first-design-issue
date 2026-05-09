/**
 * Tests for RULE-CLM-001: Claim modal offers two options.
 * Tests for RULE-CLM-004: Claim CTA available even for claimed issues.
 * SUT: ../../src/frontend/src/components/ClaimModal
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ClaimModal from "../../src/frontend/src/components/ClaimModal";

const BASE_PROPS = {
  issueUrl: "https://github.com/owner/repo/issues/1",
  claimComment: "Hey! I'd love to take this on.",
  onClose: vi.fn(),
};

describe("ClaimModal — two claim paths (RULE-CLM-001)", () => {
  it("renders the modal title", () => {
    render(<ClaimModal {...BASE_PROPS} />);
    expect(screen.getByText(/ready to claim this task/i)).toBeDefined();
  });

  it("shows a 'Go to GitHub' primary action", () => {
    render(<ClaimModal {...BASE_PROPS} />);
    expect(screen.getByRole("link", { name: /go to github/i })).toBeDefined();
  });

  it("shows a 'Copy comment' secondary action", () => {
    render(<ClaimModal {...BASE_PROPS} />);
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeDefined();
  });

  it("displays the AI-generated claim comment preview", () => {
    render(<ClaimModal {...BASE_PROPS} />);
    expect(screen.getByText(/I'd love to take this on/i)).toBeDefined();
  });

  it("has a close/cancel option", () => {
    render(<ClaimModal {...BASE_PROPS} />);
    const closeBtn = screen.getByRole("button", { name: /close|cancel/i });
    expect(closeBtn).toBeDefined();
  });

  it("calls onClose when cancel is triggered", () => {
    const onClose = vi.fn();
    render(<ClaimModal {...BASE_PROPS} onClose={onClose} />);
    fireEvent.click(screen.getByRole("button", { name: /close|cancel/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });
});

describe("ClaimModal — copy confirmation (RULE-CLM-001)", () => {
  it("shows confirmation message after copying comment", async () => {
    Object.assign(navigator, {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    });
    render(<ClaimModal {...BASE_PROPS} />);
    fireEvent.click(screen.getByRole("button", { name: /copy comment/i }));
    // Confirmation should appear (may be async; check for toast text)
    await screen.findByText(/comment copied/i);
  });
});

describe("ClaimModal — no block on claimed issues (RULE-CLM-004)", () => {
  it("renders the claim modal even when issue is already claimed", () => {
    render(<ClaimModal {...BASE_PROPS} isClaimed={true} />);
    expect(screen.getByText(/ready to claim this task/i)).toBeDefined();
    // Both actions still present — no blocking
    expect(screen.getByRole("link", { name: /go to github/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /copy comment/i })).toBeDefined();
  });
});
