# Feature: ETL Pipeline

## Context
- References: [glossary.md#etl-pipeline], [domain-model.md#issue]

## Rules

### RULE-ETL-001: Daily automated refresh
The ETL pipeline runs once daily via GitHub Actions, fetching new issues and updating existing ones.

#### Scenario: Daily run fetches new issues
- Given: The ETL ran yesterday
- And: 5 new design-related issues were created on GitHub since then
- When: Today's ETL run executes
- Then: The 5 new issues are added to the database

---

### RULE-ETL-002: Issues older than 90 days excluded on initial fetch
When fetching issues for the first time (or during reset), issues created more than 90 days ago are excluded.

#### Scenario: Old issue excluded on initial fetch
- Given: A "first-time fetch" or "reset" operation
- And: An issue was created 100 days ago
- When: The ETL processes GitHub results
- Then: The issue is not added to the database

#### Scenario: Recent issue included
- Given: A "first-time fetch" operation
- And: An issue was created 30 days ago
- When: The ETL processes GitHub results
- Then: The issue is added to the database

---

### RULE-ETL-003: Existing issues are updated
For issues already in the database, the ETL updates: description, labels, is_claimed status, updated_at, and re-runs enrichment.

#### Scenario: Issue updated on refresh
- Given: An issue exists in the database
- And: The issue's description was edited on GitHub
- When: The ETL runs
- Then: The local issue record is updated with new description
- And: Enrichment scores are recalculated

---

### RULE-ETL-004: Closed issues are archived
When an issue is detected as closed on GitHub, its status changes to "archived."

#### Scenario: Closed issue moves to archive
- Given: An issue exists with `status = active`
- And: The issue was closed on GitHub
- When: The ETL runs
- Then: The issue's status changes to "archived"
- And: The issue no longer appears in main listing

---

### RULE-ETL-005: Enrichment generates AI attributes
Each issue is enriched with AI-generated attributes: complexity_score, attractiveness_rating, seniority_level.

#### Scenario: Enrichment populates attributes
- Given: A newly fetched issue with `classification = relevant`
- When: The enrichment step runs
- Then: `complexity_score` is set to low, medium, or high
- And: `attractiveness_rating` is set (0.0 to 1.0)
- And: `seniority_level` is set to junior or senior

---

### RULE-ETL-006: Media detection
The ETL detects presence of images, videos, or external links in the issue description and sets `has_media` accordingly.

#### Scenario: Issue with image detected
- Given: An issue description containing `![screenshot](https://...)`
- When: The ETL processes the issue
- Then: `has_media = true`

#### Scenario: Issue with no media
- Given: An issue description with plain text only
- When: The ETL processes the issue
- Then: `has_media = false`
