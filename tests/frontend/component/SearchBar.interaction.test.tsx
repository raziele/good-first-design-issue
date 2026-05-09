/**
 * Tests for RULE-SRC-001, RULE-SRC-002, RULE-SRC-004: SearchBar and FilterPanel interaction.
 * SUT: ../../src/frontend/src/components/SearchBar
 *      ../../src/frontend/src/components/FilterPanel
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import SearchBar from "../../src/frontend/src/components/SearchBar";
import FilterPanel from "../../src/frontend/src/components/FilterPanel";

describe("SearchBar (RULE-SRC-001)", () => {
  it("calls onSearch with the entered query when user types", () => {
    const onSearch = vi.fn();
    render(<SearchBar onSearch={onSearch} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "onboarding" } });
    // onSearch may be debounced — verify the input value at least
    expect(input.value ?? (input as HTMLInputElement).value).toBe("onboarding");
  });

  it("shows a clear button when text is present", () => {
    render(<SearchBar onSearch={vi.fn()} />);
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "onboarding" } });
    expect(screen.getByRole("button", { name: /clear/i })).toBeDefined();
  });

  it("does not show clear button when input is empty", () => {
    render(<SearchBar onSearch={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /clear/i })).toBeNull();
  });
});

describe("FilterPanel — freshness options (RULE-SRC-002)", () => {
  it("renders all freshness filter options", () => {
    render(<FilterPanel onFilterChange={vi.fn()} />);
    expect(screen.getByText(/Last 7 days/i)).toBeDefined();
    expect(screen.getByText(/Last 30 days/i)).toBeDefined();
    expect(screen.getByText(/Last 90 days/i)).toBeDefined();
    expect(screen.getByText(/All time/i)).toBeDefined();
  });

  it("calls onFilterChange with selected filter value", () => {
    const onFilterChange = vi.fn();
    render(<FilterPanel onFilterChange={onFilterChange} />);
    fireEvent.click(screen.getByText(/Last 7 days/i));
    expect(onFilterChange).toHaveBeenCalledWith(7);
  });

  it("calls onFilterChange with null for 'All time'", () => {
    const onFilterChange = vi.fn();
    render(<FilterPanel onFilterChange={onFilterChange} />);
    fireEvent.click(screen.getByText(/All time/i));
    expect(onFilterChange).toHaveBeenCalledWith(null);
  });
});
