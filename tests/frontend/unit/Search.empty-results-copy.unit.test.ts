import { describe, expect, it } from "vitest";

import { SEARCH_NO_MATCHES_HELPER_COPYLINE } from "../../../src/frontend/src/search/issueSearchCopy.js";

describe("RULE-SRC-001 Issue search UX", () => {
  it("shows the scripted empty-results helper copyline", () => {
    expect(SEARCH_NO_MATCHES_HELPER_COPYLINE).toBe(
      "No matches — try adjusting your search terms.",
    );
  });
});
