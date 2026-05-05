# Feature: Issue Classification

## Context
- References: [glossary.md#relevant-issue], [glossary.md#not-relevant-issue], [domain-model.md#classificationresult]

## Rules

### RULE-CLS-001: Classification is fully automated
Every fetched issue is classified by an AI agent as "relevant" (UX/UI/Design work) or "not_relevant" (not design work, or already claimed).

#### Scenario: Design issue is classified as relevant
- Given: An issue with title "Create wireframes for settings page"
- And: Description contains "mockup, user flow, Figma"
- When: The classification agent processes the issue
- Then: The issue is classified as "relevant"

#### Scenario: Backend issue is classified as not relevant
- Given: An issue with title "Fix API endpoint for user auth"
- And: Description contains "database, migration, REST API"
- When: The classification agent processes the issue
- Then: The issue is classified as "not_relevant"

---

### RULE-CLS-002: Empty descriptions are not relevant
Issues with empty or placeholder-only descriptions are classified as "not_relevant."

#### Scenario: Empty description
- Given: An issue with an empty description field
- When: The classification agent processes the issue
- Then: The issue is classified as "not_relevant"

#### Scenario: Placeholder-only description
- Given: An issue where description contains only headings like "## Description\n## TODO\n## Acceptance Criteria" with no content
- When: The classification agent processes the issue
- Then: The issue is classified as "not_relevant"

---

### RULE-CLS-003: Already-claimed issues remain relevant but flagged
If an issue is design-relevant but comments indicate someone already claimed it, it remains classified as "relevant" but is flagged as `is_claimed = true`.

#### Scenario: Claimed issue flagged
- Given: A design-relevant issue
- And: A comment exists saying "I'm taking this on"
- When: The classification and enrichment runs
- Then: `classification = relevant`
- And: `is_claimed = true`

---

### RULE-CLS-004: Classification exclusion rules
Specific categories of content automatically classify as "not_relevant" regardless of design keywords.

#### Scenario Outline: Exclusion by category
- Given: An issue with content matching {exclusion_pattern}
- When: The classification agent processes the issue
- Then: The issue is classified as "not_relevant"

| exclusion_pattern |
|-------------------|
| test coverage, unit test, QA case |
| api endpoint, backend, database migration |
| refactor, rename X to Y |
| implement in code, code base for |
| sprite sheet, UTF files, game assets |

**Note:** Full exclusion rules documented in ETL implementation. This spec covers behavioral contract only.
