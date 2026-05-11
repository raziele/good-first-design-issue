import { describe, expect, it } from "vitest";

import { buildBrowseIssuesFlowPlan } from "../../../src/frontend/src/workflows/browseIssuesFlowHarness.js";

describe("browse-issues.flow Level8 UX smoke", () => {
  it("enumerates deterministic navigation beats for playwright wiring", () => {
    expect(buildBrowseIssuesFlowPlan()).toEqual(["/", "detail", "/"]);
  });
});
