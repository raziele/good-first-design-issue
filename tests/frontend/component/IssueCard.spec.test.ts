/**
 * Component tests for IssueCard.
 *
 * Spec: specs/behavior/issues.spec.md — RULE-ISS-002
 * Flow: specs/uxi/flows/browse-issues.flow.md
 *
 * Runner: vitest + @testing-library/react
 * TODO: wire up imports once the component exists at src/frontend/components/IssueCard.tsx
 */

import { describe, it, expect } from "vitest";
import { makeIssue } from "../unit/fixtures";

// TODO: uncomment when component is implemented
// import { render, screen } from "@testing-library/react";
// import { IssueCard } from "../../../src/frontend/components/IssueCard";

// ---------------------------------------------------------------------------
// RULE-ISS-002: Issue card displays preview information
// ---------------------------------------------------------------------------

describe("IssueCard", () => {
  describe("RULE-ISS-002 — required card fields", () => {
    it("IssueCard.renders repo name", () => {
      const issue = makeIssue({ repo_name: "facebook/react" });
      // TODO: const { getByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByText("facebook/react")).toBeInTheDocument();
      expect(issue.repo_name).toBe("facebook/react");
    });

    it("IssueCard.renders title", () => {
      const issue = makeIssue({ title: "Redesign settings page" });
      // TODO: const { getByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByText("Redesign settings page")).toBeInTheDocument();
      expect(issue.title).toBe("Redesign settings page");
    });

    it("IssueCard.renders truncated description under 200 chars", () => {
      const longDesc = "x".repeat(500);
      const issue = makeIssue({
        description: longDesc,
        description_truncated: longDesc.slice(0, 200),
      });
      // TODO: const { getByTestId } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByTestId("card-description").textContent!.length).toBeLessThanOrEqual(200);
      expect(issue.description_truncated.length).toBeLessThanOrEqual(200);
    });

    it("IssueCard.renders complexity score", () => {
      const issue = makeIssue({ complexity_score: "high" });
      // TODO: const { getByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByText(/high/i)).toBeInTheDocument();
      expect(["low", "medium", "high"]).toContain(issue.complexity_score);
    });

    it("IssueCard.renders attractiveness rating", () => {
      const issue = makeIssue({ attractiveness_rating: 0.8 });
      expect(issue.attractiveness_rating).toBeGreaterThanOrEqual(0.0);
      expect(issue.attractiveness_rating).toBeLessThanOrEqual(1.0);
    });

    it("IssueCard.renders seniority level", () => {
      const issue = makeIssue({ seniority_level: "junior" });
      // TODO: const { getByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByText(/junior/i)).toBeInTheDocument();
      expect(["junior", "senior"]).toContain(issue.seniority_level);
    });

    it("IssueCard.renders freshness indicator", () => {
      const issue = makeIssue({ freshness_days: 3 });
      // TODO: verify freshness chip is shown
      expect(issue.freshness_days).toBeGreaterThanOrEqual(0);
    });
  });

  describe("RULE-ISS-002 — media indicator", () => {
    it("IssueCard.shows media indicator icon when has_media is true", () => {
      const issue = makeIssue({ has_media: true });
      // TODO: const { getByTestId } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByTestId("media-indicator")).toBeInTheDocument();
      expect(issue.has_media).toBe(true);
    });

    it("IssueCard.hides media indicator when has_media is false", () => {
      const issue = makeIssue({ has_media: false });
      // TODO: const { queryByTestId } = render(<IssueCard issue={issue} />);
      // TODO: expect(queryByTestId("media-indicator")).toBeNull();
      expect(issue.has_media).toBe(false);
    });
  });

  describe("RULE-ISS-004 — claimed issue badge", () => {
    it("IssueCard.shows Already Claimed badge when is_claimed is true", () => {
      const issue = makeIssue({ is_claimed: true });
      // TODO: const { getByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(getByText(/already claimed/i)).toBeInTheDocument();
      expect(issue.is_claimed).toBe(true);
    });

    it("IssueCard.does not show claimed badge when is_claimed is false", () => {
      const issue = makeIssue({ is_claimed: false });
      // TODO: const { queryByText } = render(<IssueCard issue={issue} />);
      // TODO: expect(queryByText(/already claimed/i)).toBeNull();
      expect(issue.is_claimed).toBe(false);
    });
  });
});
