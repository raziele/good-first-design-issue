# Glossary

Project-specific terms and definitions. Referenced by behavior specs and used by agents for consistent terminology.

---

## TERM-001: Issue

A GitHub issue that describes a design-related task or gap in an open source project. In Level8, issues are the primary content unit — curated, classified, and presented to designers.

**Aliases:** Task, GitHub Issue

---

## TERM-002: Claim

The act of a designer expressing intent to work on an issue. On Level8, claiming redirects the user to GitHub with a pre-filled comment (or copies it to clipboard), signaling "I'm taking this" to the project maintainers.

**Note:** Level8 does not track claims locally. Claim status is detected by refreshing issue data from GitHub and analyzing comments.

---

## TERM-003: Designer

A UX, UI, or product designer seeking to gain experience through open source contribution. Level8's primary user persona.

**Segments:**
- Junior designers seeking portfolio pieces and first jobs
- Experienced designers pivoting to new domains

---

## TERM-004: Relevant Issue

An issue classified by Level8's automated system as genuinely related to UX/UI/Design work and not yet claimed by someone else. Only relevant issues appear in the main listing.

**Opposite:** Not Relevant Issue

---

## TERM-005: Not Relevant Issue

An issue that was fetched from GitHub but classified as not being design work (e.g., backend, testing, refactoring) or already claimed. Stored in the database but not displayed in v1.

---

## TERM-006: Complexity Score

An AI-generated rating (low / medium / high) indicating the estimated difficulty or scope of an issue. Derived from issue text analysis.

---

## TERM-007: Attractiveness Rating

An AI-generated score indicating how appealing an issue might be to designers. Factors may include: clarity of description, project popularity, learning opportunity, portfolio value.

---

## TERM-008: Seniority Level

An AI-generated classification (junior / senior) indicating whether an issue is suitable for designers with minimal experience or requires more expertise.

---

## TERM-009: Freshness

The recency of an issue, measured as days since creation or last update on GitHub. Used for filtering and prioritizing recent opportunities.

---

## TERM-010: Archive

A section containing issues that were closed on GitHub. Preserved for historical reference but not actively promoted.

---

## TERM-011: ETL Pipeline

The automated process (running daily via GitHub Actions) that fetches new issues from GitHub, updates existing issues, runs classification, and generates enrichment attributes.

---

## TERM-012: Claim Comment

An AI-generated comment that a designer can post on GitHub to signal they're taking an issue. Contextually tailored based on the issue content.

**Example:** "Hey! I'd love to take this on. I'm a designer looking to contribute — expect an update soon."
