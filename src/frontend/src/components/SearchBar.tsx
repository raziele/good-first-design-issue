/**
 * RULE-SRC-001: Search bar input triggers search against title + description.
 * RULE-SRC-004: Filter button opens filter panel/sheet.
 */

import React, { useState } from "react";

type SearchBarProps = {
  onSearch: (query: string) => void;
  onFilterChange: (filter: string) => void;
  value?: string;
  isMobile?: boolean;
};

export default function SearchBar({
  onSearch,
  onFilterChange,
  value = "",
  isMobile = false,
}: SearchBarProps) {
  const [filterOpen, setFilterOpen] = useState(false);

  function handleInput(e: React.FormEvent<HTMLInputElement>) {
    onSearch((e.target as HTMLInputElement).value);
  }

  function handleFilterClick() {
    setFilterOpen((prev) => !prev);
  }

  function handleFilterSelect(e: React.ChangeEvent<HTMLSelectElement>) {
    onFilterChange(e.target.value);
  }

  return (
    <div className="search-bar">
      <input
        type="search"
        placeholder="Search issues…"
        defaultValue={value}
        onInput={handleInput}
        className="search-bar__input"
      />
      {value && (
        <button
          data-testid="search-clear"
          className="search-bar__clear"
          onClick={() => onSearch("")}
          aria-label="Clear search"
        >
          ×
        </button>
      )}
      <button
        data-testid="filter-button"
        className="search-bar__filter-btn"
        onClick={handleFilterClick}
        aria-label="Open filters"
      >
        Filter
      </button>
      {filterOpen && (
        <div
          data-testid={isMobile ? "filter-sheet" : "filter-panel"}
          className="search-bar__filter-panel"
        >
          <select onChange={handleFilterSelect} defaultValue="all_time">
            <option value="all_time">All time</option>
            <option value="last_7_days">Last 7 days</option>
            <option value="last_30_days">Last 30 days</option>
            <option value="last_90_days">Last 90 days</option>
          </select>
        </div>
      )}
    </div>
  );
}
