/**
 * Tests for RULE-ISS-002: description truncation utility
 * SUT: src/frontend/src/utils/issueUtils.ts
 */

import { describe, it, expect } from "vitest";
import { truncateDescription } from "../../src/frontend/src/utils/issueUtils";

describe("truncateDescription — RULE-ISS-002", () => {
  it("returns short descriptions unchanged", () => {
    const desc = "Short text.";
    expect(truncateDescription(desc)).toBe(desc);
  });

  it("truncates descriptions longer than 200 chars", () => {
    const desc = "A".repeat(300);
    expect(truncateDescription(desc).length).toBeLessThanOrEqual(200);
  });

  it("appends ellipsis when truncated", () => {
    const desc = "B".repeat(300);
    expect(truncateDescription(desc)).toMatch(/\.\.\.$/);
  });

  it("does not truncate a 200-char description", () => {
    const desc = "C".repeat(200);
    const result = truncateDescription(desc);
    expect(result).toBe(desc);
  });
});
