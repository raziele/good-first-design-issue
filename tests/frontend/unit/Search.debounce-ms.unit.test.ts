import { describe, expect, it } from "vitest";

import { SEARCH_TERM_DEBOUNCE_MS } from "../../../src/frontend/src/search/searchThrottleConfig.js";

describe("search.flow RULE debounce pacing", () => {
  it("waits roughly 300ms before firing repository queries", () => {
    expect(SEARCH_TERM_DEBOUNCE_MS).toBe(300);
  });
});
