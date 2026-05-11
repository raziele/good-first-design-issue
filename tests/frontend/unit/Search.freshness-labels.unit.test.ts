import { describe, expect, it } from "vitest";

import { FRESHNESS_FILTER_DISPLAY_LABELS } from "../../../src/frontend/src/search/freshnessFilterCopy.js";

describe("RULE-SRC-002 freshness taxonomy", () => {
  it("mirrors enumerated filter badges from the Issue search spec tables", () => {
    expect(FRESHNESS_FILTER_DISPLAY_LABELS).toEqual([
      "Last 7 days",
      "Last 30 days",
      "Last 90 days",
      "All time",
    ]);
  });
});
