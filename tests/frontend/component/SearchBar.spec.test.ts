/**
 * Component tests for SearchBar and filter controls
 * Spec: specs/behavior/search.spec.md — RULE-SRC-001 to RULE-SRC-004
 * Flow: specs/uxi/flows/search.flow.md
 */

import { describe, it, expect } from "vitest";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type FreshnessFilter = "Last 7 days" | "Last 30 days" | "Last 90 days" | "All time";

interface SearchBarState {
  query: string;
  activeFilter: FreshnessFilter | null;
  clearButtonVisible: boolean;
  resultsCount: number | null;
  showBottomSheet: boolean;
}

// ---------------------------------------------------------------------------
// Stub state logic
// TODO: replace with @testing-library/react render of <SearchBar /> + <FilterBar />
// ---------------------------------------------------------------------------

function initSearchBar(): SearchBarState {
  return {
    query: "",
    activeFilter: null,
    clearButtonVisible: false,
    resultsCount: null,
    showBottomSheet: false,
  };
}

function typeQuery(state: SearchBarState, query: string): SearchBarState {
  return {
    ...state,
    query,
    clearButtonVisible: query.length > 0,
  };
}

function applyFilter(state: SearchBarState, filter: FreshnessFilter): SearchBarState {
  return { ...state, activeFilter: filter };
}

function clearAll(state: SearchBarState): SearchBarState {
  return { ...state, query: "", activeFilter: null, clearButtonVisible: false };
}

function openFilterOnMobile(state: SearchBarState): SearchBarState {
  return { ...state, showBottomSheet: true };
}

function closeFilterOnMobile(state: SearchBarState): SearchBarState {
  return { ...state, showBottomSheet: false };
}

function setResultsCount(state: SearchBarState, count: number): SearchBarState {
  return { ...state, resultsCount: count };
}

function shouldExecuteSearch(query: string): boolean {
  // Edge case from search.flow.md: < 2 chars → no search
  return query.trim().length >= 2;
}

// ---------------------------------------------------------------------------
// RULE-SRC-001: Full-text search
// ---------------------------------------------------------------------------

describe("SearchBar — RULE-SRC-001: full-text search controls", () => {
  it("SearchBar.showsClearButtonWhenQueryPresent", () => {
    /**
     * Search Active state: Clear button (×) appears when text present
     */
    const state = typeQuery(initSearchBar(), "onboarding");
    expect(state.clearButtonVisible).toBe(true);
  });

  it("SearchBar.hidesClearButtonWhenQueryEmpty", () => {
    const state = typeQuery(initSearchBar(), "");
    expect(state.clearButtonVisible).toBe(false);
  });

  it("SearchBar.noSearchExecutedForShortQuery", () => {
    /**
     * Edge case: query < 2 chars → no search executed
     */
    expect(shouldExecuteSearch("a")).toBe(false);
    expect(shouldExecuteSearch("")).toBe(false);
  });

  it("SearchBar.searchExecutedForQueryOfTwoOrMoreChars", () => {
    expect(shouldExecuteSearch("on")).toBe(true);
    expect(shouldExecuteSearch("onboarding")).toBe(true);
  });

  it("SearchBar.showsResultsCount", () => {
    /**
     * Search Active state: Results count shown e.g. "12 issues match"
     */
    let state = typeQuery(initSearchBar(), "mobile");
    state = setResultsCount(state, 12);
    expect(state.resultsCount).toBe(12);
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-002: Filter by freshness
// ---------------------------------------------------------------------------

describe("SearchBar — RULE-SRC-002: freshness filter controls", () => {
  it("SearchBar.applyingFilterSetsActiveFilter", () => {
    const state = applyFilter(initSearchBar(), "Last 7 days");
    expect(state.activeFilter).toBe("Last 7 days");
  });

  it("SearchBar.allFreshnessFilterOptionsAvailable", () => {
    const options: FreshnessFilter[] = ["Last 7 days", "Last 30 days", "Last 90 days", "All time"];
    for (const option of options) {
      const state = applyFilter(initSearchBar(), option);
      expect(state.activeFilter).toBe(option);
    }
  });

  it("SearchBar.clearFilterResetsActiveFilter", () => {
    let state = applyFilter(initSearchBar(), "Last 30 days");
    state = clearAll(state);
    expect(state.activeFilter).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-003: Search and filter combine
// ---------------------------------------------------------------------------

describe("SearchBar — RULE-SRC-003: combined search + filter state", () => {
  it("SearchBar.canHaveBothQueryAndFilterActive", () => {
    let state = typeQuery(initSearchBar(), "mobile");
    state = applyFilter(state, "Last 7 days");
    expect(state.query).toBe("mobile");
    expect(state.activeFilter).toBe("Last 7 days");
  });

  it("SearchBar.clearAllResetsQueryAndFilter", () => {
    let state = typeQuery(initSearchBar(), "mobile");
    state = applyFilter(state, "Last 30 days");
    state = clearAll(state);
    expect(state.query).toBe("");
    expect(state.activeFilter).toBeNull();
  });
});

// ---------------------------------------------------------------------------
// RULE-SRC-004: Mobile uses bottom sheet for filters
// ---------------------------------------------------------------------------

describe("SearchBar — RULE-SRC-004: mobile bottom sheet", () => {
  it("SearchBar.tapFilterButtonOpensBottomSheetOnMobile", () => {
    /**
     * Scenario: Filter interaction on mobile
     * Given a user is on a mobile device
     * When the user taps the filter button
     * Then a bottom sheet slides up with filter options
     */
    const state = openFilterOnMobile(initSearchBar());
    expect(state.showBottomSheet).toBe(true);
  });

  it("SearchBar.dismissingBottomSheetClosesIt", () => {
    let state = openFilterOnMobile(initSearchBar());
    state = closeFilterOnMobile(state);
    expect(state.showBottomSheet).toBe(false);
  });
});

// ---------------------------------------------------------------------------
// Browse flow edge cases (browse-issues.flow.md + search.flow.md)
// ---------------------------------------------------------------------------

describe("SearchBar — edge cases from flow specs", () => {
  it("SearchBar.specialCharactersInQueryDoNotCrash", () => {
    /**
     * Edge case: special characters in search → escaped, search proceeds normally
     */
    const queries = ["mobile & icons", "design | layout", "(settings)", "user[0]"];
    for (const q of queries) {
      expect(() => shouldExecuteSearch(q)).not.toThrow();
    }
  });
});
