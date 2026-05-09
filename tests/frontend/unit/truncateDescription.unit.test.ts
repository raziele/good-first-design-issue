/**
 * Tests for RULE-ISS-002: description_truncated derived attribute.
 * SUT: ../../src/frontend/src/utils/truncateDescription
 */
import { describe, it, expect } from "vitest";
import { truncateDescription } from "../../src/frontend/src/utils/truncateDescription";

describe("truncateDescription (RULE-ISS-002)", () => {
  it("truncates descriptions longer than 200 characters", () => {
    const longDesc = "A".repeat(250);
    const result = truncateDescription(longDesc);
    expect(result.length).toBeLessThanOrEqual(203); // 200 + "..."
    expect(result.endsWith("...")).toBe(true);
  });

  it("does not truncate descriptions at or under 200 characters", () => {
    const shortDesc = "Short description.";
    const result = truncateDescription(shortDesc);
    expect(result).toBe(shortDesc);
    expect(result.endsWith("...")).toBe(false);
  });

  it("does not truncate a description of exactly 200 characters", () => {
    const exactDesc = "B".repeat(200);
    const result = truncateDescription(exactDesc);
    expect(result).toBe(exactDesc);
  });
});
