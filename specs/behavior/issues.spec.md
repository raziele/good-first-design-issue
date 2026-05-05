# Feature: Issue Browsing and Viewing

## Context
- References: [glossary.md#issue], [glossary.md#relevant-issue], [domain-model.md#issue]
- UXI Flow: [flows/browse-issues.flow.md], [flows/claim-issue.flow.md]

## Rules

### RULE-ISS-001: Display only relevant active issues
Only issues with `classification = relevant` AND `status = active` appear in the main listing.

#### Scenario: Relevant active issue appears in listing
- Given: An issue with classification "relevant" and status "active"
- When: A user views the main issue listing
- Then: The issue appears in the listing

#### Scenario: Not-relevant issue is hidden
- Given: An issue with classification "not_relevant"
- When: A user views the main issue listing
- Then: The issue does not appear

#### Scenario: Archived issue is hidden from main listing
- Given: An issue with status "archived"
- When: A user views the main issue listing
- Then: The issue does not appear

---

### RULE-ISS-002: Issue card displays preview information
Each issue card shows: repo name, title, truncated description, key scores (complexity, attractiveness, seniority level, freshness), and a media indicator if applicable.

#### Scenario: Card shows required elements
- Given: A relevant active issue with all attributes populated
- When: The issue is rendered as a card
- Then: The card displays repo name, title, truncated description (~200 chars), complexity score, attractiveness rating, seniority level, freshness indicator
- And: If `has_media = true`, a media indicator icon is shown

---

### RULE-ISS-003: Issue detail view shows full information
Clicking an issue card opens a detail view with: full description, all scores, repo stars, and a link to the GitHub issue.

#### Scenario: Detail view shows full description
- Given: A user clicks on an issue card
- When: The detail view loads
- Then: The full issue description is displayed (not truncated)
- And: All attribute scores are visible
- And: Repo star count is visible
- And: A direct link to the GitHub issue is provided

#### Scenario: Media is indicated but not embedded
- Given: An issue with `has_media = true`
- When: The user views the detail page
- Then: A media indicator is shown
- But: Images/videos are not embedded; user must visit GitHub to view

---

### RULE-ISS-004: Claimed issues are marked
Issues detected as already claimed (via GitHub comment analysis) are shown but visually marked as "already claimed."

#### Scenario: Claimed issue displays claim badge
- Given: An issue with `is_claimed = true`
- When: The issue appears in the listing or detail view
- Then: A visual indicator shows "Already claimed"
- And: The claim CTA is still available (user can still attempt to claim)

---

### RULE-ISS-005: Default sort is by freshness
Issues are sorted by freshness (most recent first) by default.

#### Scenario: Listing default sort order
- Given: Multiple relevant active issues with different freshness values
- When: A user views the main listing without applying filters
- Then: Issues are sorted by `freshness_days` ascending (newest first)
