# Spec Schema — Authoring Conventions

## Purpose

This document defines the contract for writing specs in this project. All behavior specs, UXI flows, and domain chapters must follow these conventions so Agent 1 can reliably generate tests.

---

## Behavior Specs (`specs/behavior/*.spec.md`)

### Structure

```markdown
# Feature: <Feature Name>

## Context
- References: [glossary.md#<term>], [domain-model.md#<entity>]
- UXI Flow: [flows/<flow-name>.flow.md]

## Rules

### RULE-<DOMAIN>-<NNN>: <Short description>
<Prose explanation of the rule.>

#### Scenario: <Scenario name>
- Given: <precondition>
- When: <action>
- Then: <expected outcome>
```

### Conventions

1. **Stable IDs** — Every rule gets a unique ID in the format `RULE-<DOMAIN>-<NNN>` (e.g., `RULE-AUTH-001`). IDs are never reused, even if a rule is deleted.
2. **Given/When/Then** — Every scenario uses this format for unambiguous test generation.
3. **Cross-references** — Link to glossary terms and UXI flows where applicable.
4. **One feature per file** — Each `.spec.md` file covers a single feature area.
5. **Ambiguity markers** — If a scenario is unclear, mark it with `<!-- AMBIGUOUS: reason -->` so Agent 1 generates a `TODO` test.

---

## UXI Flows (`specs/uxi/flows/*.flow.md`)

### Structure

```markdown
# Flow: <Flow Name>

## Steps
1. <Step description>
2. <Step description>
...

## States
- Loading: <description>
- Error: <description>
- Success: <description>

## Edge Cases
- <Edge case> -> <expected behavior>
```

---

## Domain Chapters (`specs/chapters/`)

- `glossary.md` — Project-specific terms and definitions. Format: `## Term\n<Definition>`
- `domain-model.md` — Entity relationships, invariants, and constraints.
- Additional chapters as needed for domain knowledge.

---

## API Contracts (`specs/api/`)

- REST: `openapi.yaml` following OpenAPI 3.x spec
- GraphQL: `graphql.schema.graphql` (if applicable)

---

## Brand (`specs/brand/`)

- `voice-and-tone.md` — Writing style, terminology preferences, error message tone
- `visual-identity.md` — Colors, typography, spacing tokens (if applicable)
