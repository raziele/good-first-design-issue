import { describe, expect, it } from "vitest";

import { claimIssueWorkbenchSteps } from "../../../src/frontend/src/workflows/claimIssueWorkbench.js";

describe("claim-issue.flow orchestration seeds", () => {
  it("lists claim option beats for future browser automation", () => {
    expect(claimIssueWorkbenchSteps()).toEqual(["open_sheet", "github", "clipboard"]);
  });
});
