import { describe, expect, it } from "vitest";

import { CLAIM_CLIPBOARD_TOAST_COPY } from "../../../src/frontend/src/claim/clipboardSignals.js";

describe("claim-issue.flow clipboard confirmation", () => {
  it("surfaces the toast copy designers expect after copying", () => {
    expect(CLAIM_CLIPBOARD_TOAST_COPY).toBe("Comment copied!");
  });
});
