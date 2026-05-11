/**
 * Tests for RULE-CLM-001: Claim action offers two options (Go to GitHub / Copy comment)
 * Tests for RULE-CLM-002: Claim comment is AI-generated (contextual, non-fixed)
 * SUT: src/frontend/src/components/ClaimModal.tsx
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import ClaimModal from "../../src/frontend/src/components/ClaimModal";

const baseProps = {
  issue: {
    id: "1",
    title: "Mobile onboarding redesign",
    github_url: "https://github.com/org/repo/issues/1",
    claim_comment: "Hey! I'd love to work on the onboarding flow redesign.",
  },
  onClose: vi.fn(),
};

let container: HTMLDivElement;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
});

afterEach(() => {
  document.body.removeChild(container);
});

function render(element: React.ReactElement) {
  act(() => {
    createRoot(container).render(element);
  });
}

describe("ClaimModal — RULE-CLM-001", () => {
  it("renders the modal title", () => {
    render(createElement(ClaimModal, baseProps));
    expect(container.textContent).toMatch(/ready to claim this task/i);
  });

  it("shows a 'Go to GitHub' primary action button", () => {
    render(createElement(ClaimModal, baseProps));
    const btn = container.querySelector("[data-testid='go-to-github']");
    expect(btn).not.toBeNull();
  });

  it("shows a 'Copy comment' secondary action button", () => {
    render(createElement(ClaimModal, baseProps));
    const btn = container.querySelector("[data-testid='copy-comment']");
    expect(btn).not.toBeNull();
  });

  it("the Go to GitHub button links to the correct GitHub URL", () => {
    render(createElement(ClaimModal, baseProps));
    const link = container.querySelector("[data-testid='go-to-github']") as HTMLAnchorElement | null;
    expect(link?.href).toContain("github.com/org/repo/issues/1");
  });

  it("renders a preview of the AI-generated claim comment", () => {
    render(createElement(ClaimModal, baseProps));
    expect(container.textContent).toContain(baseProps.issue.claim_comment);
  });

  it("has a close/cancel option", () => {
    render(createElement(ClaimModal, baseProps));
    const close = container.querySelector("[data-testid='modal-close']");
    expect(close).not.toBeNull();
  });
});

describe("ClaimModal — RULE-CLM-002", () => {
  it("claim comment is passed from props (contextually generated, not a fixed template)", () => {
    const customComment = "I'll specifically work on the mobile onboarding flow.";
    const props = {
      ...baseProps,
      issue: { ...baseProps.issue, claim_comment: customComment },
    };
    render(createElement(ClaimModal, props));
    expect(container.textContent).toContain(customComment);
  });
});
