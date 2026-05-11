import { describe, expect, it } from "vitest";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { IssueCard } from "../../../src/frontend/src/issue/IssueCard.jsx";

describe("RULE-ISS-002 Issue card preview chrome", () => {
  it("renders repo, title, complexity, attractiveness, seniority, freshness, and media cues", () => {
    const markup = renderToStaticMarkup(
      createElement(IssueCard, {
        repoName: "acme/mobile-shell",
        title: "Refresh contributor onboarding illustrations",
        descriptionPreview: "Prototype empty states for the mobile shell experience.",
        complexityScore: "medium",
        attractivenessRating: 0.82,
        seniorityLevel: "junior",
        freshnessLabel: "3d",
        hasMedia: true,
      }),
    );
    expect(markup).toContain("acme/mobile-shell");
    expect(markup).toContain("Refresh contributor onboarding illustrations");
    expect(markup).toContain("Medium");
    expect(markup).toContain("0.82");
    expect(markup).toContain("Junior");
    expect(markup).toContain("3d");
    expect(markup).toContain("Media");
  });
});
