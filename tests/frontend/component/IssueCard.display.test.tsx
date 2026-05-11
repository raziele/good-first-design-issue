/**
 * Tests for RULE-ISS-002: IssueCard displays required preview information
 * Tests for RULE-ISS-004: Claimed issues are marked with a visual indicator
 * SUT: src/frontend/src/components/IssueCard.tsx
 */

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import IssueCard from "../../src/frontend/src/components/IssueCard";

const baseIssue = {
  id: "1",
  repo_name: "org/awesome-project",
  title: "Redesign onboarding flow",
  description_truncated: "A truncated description for the card preview.",
  complexity_score: "low" as const,
  attractiveness_rating: 0.85,
  seniority_level: "junior" as const,
  freshness_days: 3,
  has_media: false,
  is_claimed: false,
  github_url: "https://github.com/org/awesome-project/issues/1",
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

describe("IssueCard — RULE-ISS-002", () => {
  it("displays the repo name", () => {
    render(createElement(IssueCard, { issue: baseIssue }));
    expect(container.textContent).toContain("org/awesome-project");
  });

  it("displays the issue title", () => {
    render(createElement(IssueCard, { issue: baseIssue }));
    expect(container.textContent).toContain("Redesign onboarding flow");
  });

  it("displays the truncated description", () => {
    render(createElement(IssueCard, { issue: baseIssue }));
    expect(container.textContent).toContain("A truncated description for the card preview.");
  });

  it("displays the complexity score", () => {
    render(createElement(IssueCard, { issue: { ...baseIssue, complexity_score: "medium" } }));
    expect(container.textContent).toMatch(/medium/i);
  });

  it("displays the seniority level", () => {
    render(createElement(IssueCard, { issue: baseIssue }));
    expect(container.textContent).toMatch(/junior/i);
  });

  it("displays a freshness indicator", () => {
    render(createElement(IssueCard, { issue: baseIssue }));
    // Freshness must be visible in some form — days value or label
    expect(container.textContent).toMatch(/3/);
  });

  it("shows a media indicator icon when has_media is true", () => {
    render(createElement(IssueCard, { issue: { ...baseIssue, has_media: true } }));
    const mediaIndicator = container.querySelector("[data-testid='media-indicator']");
    expect(mediaIndicator).not.toBeNull();
  });

  it("does not show a media indicator when has_media is false", () => {
    render(createElement(IssueCard, { issue: { ...baseIssue, has_media: false } }));
    const mediaIndicator = container.querySelector("[data-testid='media-indicator']");
    expect(mediaIndicator).toBeNull();
  });
});

describe("IssueCard — RULE-ISS-004", () => {
  it("shows 'Already claimed' badge when is_claimed is true", () => {
    render(createElement(IssueCard, { issue: { ...baseIssue, is_claimed: true } }));
    expect(container.textContent).toMatch(/already claimed/i);
  });

  it("does not show claimed badge when is_claimed is false", () => {
    render(createElement(IssueCard, { issue: { ...baseIssue, is_claimed: false } }));
    expect(container.textContent).not.toMatch(/already claimed/i);
  });
});
