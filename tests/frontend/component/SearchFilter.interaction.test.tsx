/**
 * Tests for Search and Filter component rules.
 * RULE-SRC-001: Full-text search across title and description
 * RULE-SRC-002: Filter by freshness
 * RULE-SRC-003: Search and filter combine (AND logic)
 * RULE-SRC-004: Mobile uses bottom sheet for filters
 */

import { describe, it, expect, vi, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor, cleanup } from "@testing-library/react";

afterEach(cleanup);
import { SearchFilterBar } from "../../src/frontend/src/components/SearchFilterBar";

describe("SearchFilterBar — RULE-SRC-001: full-text search", () => {
  it("calls onSearch with the entered query after debounce", async () => {
    vi.useFakeTimers();
    const onSearch = vi.fn();
    render(<SearchFilterBar onSearch={onSearch} onFilterChange={() => {}} />);
    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "onboarding" } });
    vi.advanceTimersByTime(300);
    await waitFor(() => expect(onSearch).toHaveBeenCalledWith("onboarding"));
    vi.useRealTimers();
  });

  it("shows clear button (×) when search text is present", () => {
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={() => {}} />);
    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "something" } });
    expect(screen.getByRole("button", { name: /clear|×/i })).toBeTruthy();
  });

  it("does not fire search for queries shorter than 2 chars", async () => {
    vi.useFakeTimers();
    const onSearch = vi.fn();
    render(<SearchFilterBar onSearch={onSearch} onFilterChange={() => {}} />);
    const input = screen.getByRole("searchbox");
    fireEvent.change(input, { target: { value: "a" } });
    vi.advanceTimersByTime(300);
    await waitFor(() => expect(onSearch).not.toHaveBeenCalled());
    vi.useRealTimers();
  });
});

describe("SearchFilterBar — RULE-SRC-002: freshness filter options", () => {
  it.each([
    ["Last 7 days", 7],
    ["Last 30 days", 30],
    ["Last 90 days", 90],
    ["All time", null],
  ])("renders '%s' filter option", (label) => {
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={() => {}} />);
    expect(screen.getByText(new RegExp(label, "i"))).toBeTruthy();
  });

  it("calls onFilterChange with correct days when 'Last 7 days' is selected", () => {
    const onFilterChange = vi.fn();
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={onFilterChange} />);
    fireEvent.click(screen.getByText(/last 7 days/i));
    expect(onFilterChange).toHaveBeenCalledWith({ maxFreshnessDays: 7 });
  });

  it("calls onFilterChange with null when 'All time' is selected", () => {
    const onFilterChange = vi.fn();
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={onFilterChange} />);
    fireEvent.click(screen.getByText(/all time/i));
    expect(onFilterChange).toHaveBeenCalledWith({ maxFreshnessDays: null });
  });
});

describe("SearchFilterBar — RULE-SRC-004: mobile bottom sheet for filters", () => {
  it("renders a filter trigger button on mobile viewport", () => {
    // Simulate mobile viewport
    Object.defineProperty(window, "innerWidth", { writable: true, configurable: true, value: 375 });
    window.dispatchEvent(new Event("resize"));
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={() => {}} isMobile={true} />);
    expect(screen.getByRole("button", { name: /filter/i })).toBeTruthy();
  });

  it("opens bottom sheet when filter button is tapped on mobile", () => {
    render(<SearchFilterBar onSearch={() => {}} onFilterChange={() => {}} isMobile={true} />);
    fireEvent.click(screen.getByRole("button", { name: /filter/i }));
    expect(screen.getByTestId("bottom-sheet")).toBeTruthy();
  });
});
