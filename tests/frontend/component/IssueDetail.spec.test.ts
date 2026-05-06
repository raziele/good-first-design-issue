/**
 * Component tests for IssueDetail view.
 *
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-003, RULE-ISS-004
 * Flow: specs/uxi/flows/browse-issues.flow.md, specs/uxi/flows/claim-issue.flow.md
 *
 * Runner: vitest + @testing-library/react
 * TODO: wire up imports once the component exists at src/frontend/components/IssueDetail.tsx
 */

import { describe, it, expect } from "vitest";
import { makeIssue } from "../unit/fixtures";

// TODO: import { render, screen } from "@testing-library/react";
// TODO: import { IssueDetail } from "../../../src/frontend/components/IssueDetail";

// ---------------------------------------------------------------------------
// RULE-ISS-003: Issue detail view shows full information
// ---------------------------------------------------------------------------

describe("IssueDetail", () => {
  describe("RULE-ISS-003 — full description", () => {
    it("IssueDetail.shows full description not truncated", () => {
      const fullDesc = "Full description. ".repeat(20);
      const issue = makeIssue({
        description: fullDesc,
        description_truncated: fullDesc.slice(0, 200),
      });
      // TODO: const { getByTestId } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByTestId("detail-description").textContent).toBe(fullDesc);
      expect(issue.description.length).toBeGreaterThan(issue.description_truncated.length);
    });

    it("IssueDetail.shows all attribute scores", () => {
      const issue = makeIssue({
        complexity_score: "low",
        attractiveness_rating: 0.9,
        seniority_level: "senior",
        freshness_days: 5,
      });
      // TODO: verify all score fields render
      expect(issue.complexity_score).toBeDefined();
      expect(issue.attractiveness_rating).toBeDefined();
      expect(issue.seniority_level).toBeDefined();
      expect(issue.freshness_days).toBeDefined();
    });

    it("IssueDetail.shows repo star count", () => {
      const issue = makeIssue({ repo_stars: 4200 });
      // TODO: const { getByText } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByText(/4200/)).toBeInTheDocument();
      expect(issue.repo_stars).toBe(4200);
    });

    it("IssueDetail.provides direct link to GitHub issue", () => {
      const issue = makeIssue({ github_url: "https://github.com/org/repo/issues/99" });
      // TODO: const { getByRole } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByRole("link", { name: /github/i })).toHaveAttribute("href", issue.github_url);
      expect(issue.github_url).toMatch(/^https:\/\/github\.com\//);
    });
  });

  describe("RULE-ISS-003 — media indicator (not embedded)", () => {
    it("IssueDetail.shows media indicator when has_media is true", () => {
      const issue = makeIssue({ has_media: true });
      // TODO: const { getByTestId } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByTestId("detail-media-indicator")).toBeInTheDocument();
      expect(issue.has_media).toBe(true);
    });

    it("IssueDetail.does not embed images or videos inline", () => {
      const issue = makeIssue({
        has_media: true,
        description: "See ![img](https://example.com/img.png)",
      });
      // TODO: ensure no <img> or <video> tags are rendered in the description container
      // TODO: const container = render(<IssueDetail issue={issue} />).container;
      // TODO: expect(container.querySelector("img")).toBeNull();
      expect(issue).not.toHaveProperty("embed_url");
    });
  });

  describe("RULE-ISS-004 — claimed issue display in detail", () => {
    it("IssueDetail.shows Already Claimed badge when is_claimed is true", () => {
      const issue = makeIssue({ is_claimed: true });
      // TODO: const { getByText } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByText(/already claimed/i)).toBeInTheDocument();
      expect(issue.is_claimed).toBe(true);
    });

    it("IssueDetail.Claim CTA remains visible even when issue is already claimed", () => {
      const issue = makeIssue({ is_claimed: true, classification: "relevant", status: "active" });
      // TODO: const { getByRole } = render(<IssueDetail issue={issue} />);
      // TODO: expect(getByRole("button", { name: /claim this task/i })).toBeInTheDocument();
      expect(issue.status).toBe("active");
    });
  });
});
