/**
 * Tests for RULE-SRC-001: Search bar input triggers search against title + description
 * Tests for RULE-SRC-004: Mobile uses bottom sheet for filters
 * SUT: src/frontend/src/components/SearchBar.tsx
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import SearchBar from "../../src/frontend/src/components/SearchBar";

let container: HTMLDivElement;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
});

afterEach(() => {
  document.body.removeChild(container);
});

function render(element: React.ReactElement) {
  act(() => {
    createRoot(container).render(element);
  });
}

describe("SearchBar — RULE-SRC-001", () => {
  it("renders a search input element", () => {
    render(createElement(SearchBar, { onSearch: vi.fn(), onFilterChange: vi.fn() }));
    const input = container.querySelector("input[type='search'], input[type='text']");
    expect(input).not.toBeNull();
  });

  it("calls onSearch with the current query when input changes", () => {
    const onSearch = vi.fn();
    render(createElement(SearchBar, { onSearch, onFilterChange: vi.fn() }));
    const input = container.querySelector("input") as HTMLInputElement;
    act(() => {
      input.value = "accessibility";
      input.dispatchEvent(new Event("input", { bubbles: true }));
    });
    expect(onSearch).toHaveBeenCalledWith("accessibility");
  });

  it("shows a clear (×) button when the search input has text", () => {
    const onSearch = vi.fn();
    render(createElement(SearchBar, { onSearch, onFilterChange: vi.fn(), value: "hello" }));
    const clearBtn = container.querySelector("[data-testid='search-clear']");
    expect(clearBtn).not.toBeNull();
  });

  it("does not show the clear button when input is empty", () => {
    render(createElement(SearchBar, { onSearch: vi.fn(), onFilterChange: vi.fn(), value: "" }));
    const clearBtn = container.querySelector("[data-testid='search-clear']");
    expect(clearBtn).toBeNull();
  });
});

describe("SearchBar — RULE-SRC-004", () => {
  it("renders a filter button", () => {
    render(createElement(SearchBar, { onSearch: vi.fn(), onFilterChange: vi.fn() }));
    const filterBtn = container.querySelector("[data-testid='filter-button']");
    expect(filterBtn).not.toBeNull();
  });

  it("opens the filter sheet/dropdown when filter button is clicked", () => {
    render(
      createElement(SearchBar, {
        onSearch: vi.fn(),
        onFilterChange: vi.fn(),
        isMobile: false,
      })
    );
    const filterBtn = container.querySelector("[data-testid='filter-button']") as HTMLElement;
    act(() => {
      filterBtn.click();
    });
    const filterPanel = container.querySelector(
      "[data-testid='filter-panel'], [data-testid='filter-sheet']"
    );
    expect(filterPanel).not.toBeNull();
  });
});
