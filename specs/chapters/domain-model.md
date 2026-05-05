# Domain Model

Entity relationships, invariants, and constraints for Level8.

---

## ENTITY-001: Issue

The core content entity representing a GitHub issue related to design work.

### Attributes

| Attribute | Type | Source | Description |
|-----------|------|--------|-------------|
| `id` | string | GitHub | GitHub issue ID (unique identifier) |
| `github_url` | url | GitHub | Direct link to the issue on GitHub |
| `repo_name` | string | GitHub | Repository name (owner/repo format) |
| `repo_stars` | integer | GitHub | Star count of the repository |
| `title` | string | GitHub | Issue title |
| `description` | text | GitHub | Full issue body/description |
| `description_truncated` | text | Derived | First ~200 chars for card preview |
| `labels` | string[] | GitHub | GitHub labels on the issue |
| `has_media` | boolean | Derived | True if description contains images, videos, or external links |
| `created_at` | datetime | GitHub | When the issue was created |
| `updated_at` | datetime | GitHub | When the issue was last updated |
| `freshness_days` | integer | Derived | Days since created_at |
| `classification` | enum | AI | `relevant` or `not_relevant` |
| `is_claimed` | boolean | Derived | True if comments indicate someone claimed it |
| `complexity_score` | enum | AI | `low`, `medium`, `high` |
| `attractiveness_rating` | float | AI | 0.0 to 1.0 scale |
| `seniority_level` | enum | AI | `junior`, `senior` |
| `status` | enum | System | `active`, `closed`, `archived` |
| `fetched_at` | datetime | System | Last time data was refreshed from GitHub |

### Invariants

- `id` is unique across all issues
- `classification = relevant` required for display in main listing
- `status = active` required for display in main listing (archived issues shown separately)
- Issues older than 90 days at fetch time are excluded from initial fetch

### Relationships

- Belongs to one Repository (denormalized as `repo_name`, `repo_stars`)

---

## ENTITY-002: Repository

Denormalized repository information, stored as attributes on Issue.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `repo_name` | string | Full name (owner/repo) |
| `repo_stars` | integer | Star count |

**Note:** In v1, repository is not a separate entity — data is denormalized onto Issue. May be normalized if we add repo-level features later.

---

## ENTITY-003: ClassificationResult (internal)

Stored result of the automated classification process.

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `issue_id` | string | Reference to Issue |
| `classification` | enum | `relevant`, `not_relevant` |
| `confidence` | float | 0.0 to 1.0 |
| `reason` | text | Explanation for classification |
| `classified_at` | datetime | When classification ran |

**Note:** Primarily for debugging and potential future human review. Not exposed in UI.
