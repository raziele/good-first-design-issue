/**
 * Tests for RULE-CLM-001: GitHub redirect URL construction for claiming.
 * SUT: ../../src/frontend/src/utils/buildGitHubClaimUrl
 */
import { describe, it, expect } from "vitest";
import { buildGitHubClaimUrl } from "../../src/frontend/src/utils/buildGitHubClaimUrl";

describe("buildGitHubClaimUrl (RULE-CLM-001)", () => {
  const ISSUE_URL = "https://github.com/owner/repo/issues/42";
  const COMMENT = "Hey! I'd love to take this on.";

  it("includes the issue URL in the generated link", () => {
    const url = buildGitHubClaimUrl(ISSUE_URL, COMMENT);
    expect(url).toContain("github.com/owner/repo/issues/42");
  });

  it("includes a body query parameter for the pre-filled comment", () => {
    const url = buildGitHubClaimUrl(ISSUE_URL, COMMENT);
    expect(url).toContain("body=");
  });

  it("returns a valid HTTPS URL", () => {
    const url = buildGitHubClaimUrl(ISSUE_URL, COMMENT);
    expect(url.startsWith("https://")).toBe(true);
  });

  it("URL-encodes the comment body", () => {
    const url = buildGitHubClaimUrl(ISSUE_URL, "Hello world!");
    // Space must be encoded
    expect(url).not.toContain("Hello world!");
  });
});
