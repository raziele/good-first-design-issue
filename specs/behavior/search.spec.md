# Feature: Search and Filtering

## Context
- References: [glossary.md#issue], [glossary.md#freshness]
- UXI Flow: [flows/search.flow.md]

## Rules

### RULE-SRC-001: Full-text search across title and description
Users can search issues by entering text. Search matches against issue title and description.

#### Scenario: Search matches title
- Given: An issue with title "Mobile onboarding redesign"
- When: A user searches for "onboarding"
- Then: The issue appears in search results

#### Scenario: Search matches description
- Given: An issue with description containing "accessibility audit"
- When: A user searches for "accessibility"
- Then: The issue appears in search results

#### Scenario: Search returns no results
- Given: No issues contain the word "blockchain"
- When: A user searches for "blockchain"
- Then: An empty state is shown with message "No matches — try adjusting your search terms."

---

### RULE-SRC-002: Filter by freshness
Users can filter issues by freshness (recency). This is the only filter dimension in v1.

#### Scenario: Filter to recent issues
- Given: Issues with various freshness values
- When: A user applies a "Last 7 days" freshness filter
- Then: Only issues with `freshness_days <= 7` are shown

#### Scenario Outline: Freshness filter options
- Given: Multiple issues with varying freshness
- When: A user selects freshness filter {filter_value}
- Then: Only issues matching the criteria are shown

| filter_value | criteria |
|--------------|----------|
| Last 7 days | freshness_days <= 7 |
| Last 30 days | freshness_days <= 30 |
| Last 90 days | freshness_days <= 90 |
| All time | no filter applied |

---

### RULE-SRC-003: Search and filter combine
Search terms and freshness filter are combined (AND logic).

#### Scenario: Combined search and filter
- Given: An issue titled "Mobile redesign" created 3 days ago
- And: An issue titled "Mobile app icons" created 45 days ago
- When: A user searches "mobile" and filters to "Last 7 days"
- Then: Only "Mobile redesign" appears in results

---

### RULE-SRC-004: Mobile uses bottom sheet for filters
On mobile viewports, filters are accessed via a bottom sheet modal.

#### Scenario: Filter interaction on mobile
- Given: A user is on a mobile device
- When: The user taps the filter button
- Then: A bottom sheet slides up with filter options
