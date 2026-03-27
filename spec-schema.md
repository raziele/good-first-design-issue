# Spec Schema — How to Write Specs for This Project

This document defines the conventions, structure, and rules for all specification
documents in the `specs/` directory. It is the contract between the human author
and Agent 1 (Test Generator). If a spec does not follow this schema, Agent 1 may
produce incorrect, incomplete, or ambiguous tests.

Every agent reads this file as part of its context.

---

## 1. General Principles

### 1.1 Specs Are the Source of Truth

Code is generated to satisfy tests. Tests are generated from specs. Therefore,
specs must be **complete, unambiguous, and self-consistent**. If something is not
in the specs, it does not exist in the system.

### 1.2 Precision over Brevity

A longer, unambiguous spec is better than a short, vague one. When in doubt,
add a scenario. Every edge case you think of should be written down — if you
don't write it, no test will cover it and no code will handle it.

### 1.3 Stable Identifiers

Every testable rule, scenario, flow, and API endpoint has a stable ID. These IDs:
- Never change once assigned (even if the content changes)
- Are never reused after deletion
- Follow the naming conventions defined in Section 3
- Are used by Agent 1 to maintain the spec-to-test mapping manifest

### 1.4 Cross-References

Specs reference other specs by file path and ID. This creates a traceable graph
from domain concepts → behavior rules → UXI flows → API contracts.

Format: `[glossary.md#term-name]` or `[auth.spec.md#RULE-AUTH-001]`

---

## 2. File Organization

### 2.1 Directory Structure

```
specs/
├── behavior/          # What the system does (rules + scenarios)
│   └── {domain}.spec.md
├── chapters/          # Domain knowledge (referenced by behavior specs)
│   ├── glossary.md
│   ├── domain-model.md
│   └── {topic}.md
├── uxi/               # User experience & interaction
│   ├── flows/
│   │   └── {flow-name}.flow.md
│   ├── design-tokens.md       (optional)
│   └── interactions.md        (optional)
├── api/                # Machine-readable contracts
│   ├── openapi.yaml
│   └── {other-contracts}
├── brand/              # Voice, tone, visual identity
│   ├── voice-and-tone.md
│   └── visual-identity.md
└── spec-schema.md      # This file
```

### 2.2 File Naming

- Behavior specs: `{domain}.spec.md` (e.g., `auth.spec.md`, `checkout.spec.md`)
- Chapters: `{topic}.md` (e.g., `glossary.md`, `domain-model.md`)
- UXI flows: `{flow-name}.flow.md` (e.g., `onboarding.flow.md`)
- Use lowercase kebab-case for all filenames

---

## 3. Identifier Conventions

### 3.1 Behavior Rule IDs

Format: `RULE-{DOMAIN}-{NNN}`

- `{DOMAIN}`: uppercase short code for the feature domain (e.g., AUTH, CART, PAY)
- `{NNN}`: zero-padded three-digit sequential number

Examples: `RULE-AUTH-001`, `RULE-CART-012`, `RULE-PAY-003`

### 3.2 Scenario IDs

Format: `{RULE-ID}.S{NN}`

Scenarios are scoped to their parent rule.

Examples: `RULE-AUTH-001.S01`, `RULE-AUTH-001.S02`

### 3.3 UXI Flow IDs

Format: `FLOW-{NAME}-{NNN}`

Examples: `FLOW-ONBOARD-001`, `FLOW-CHECKOUT-002`

### 3.4 UXI Flow Step IDs

Format: `{FLOW-ID}.STEP-{NN}`

Examples: `FLOW-ONBOARD-001.STEP-01`, `FLOW-ONBOARD-001.STEP-02`

### 3.5 API Endpoint IDs

Format: `API-{METHOD}-{RESOURCE}-{NNN}`

Examples: `API-POST-USERS-001`, `API-GET-ORDERS-002`

### 3.6 Glossary Term IDs

Format: `TERM-{NAME}`

Use the kebab-case term name as the ID.

Examples: `TERM-session`, `TERM-cart-item`, `TERM-fulfillment-window`

### 3.7 Domain Model Entity IDs

Format: `ENTITY-{NAME}`

Examples: `ENTITY-user`, `ENTITY-order`, `ENTITY-product`

---

## 4. Behavior Spec Format

Behavior specs are the primary input for test generation.

### 4.1 Document Structure

```markdown
# Feature: {Feature Name}

## Metadata
- Domain: {DOMAIN-CODE}
- Status: [draft | review | stable | deprecated]
- Last Updated: {YYYY-MM-DD}
- Dependencies: [{other-spec-file}#ID, ...]

## Context
Brief description of what this feature does and why it exists.
Reference domain terms: [glossary.md#TERM-x], [domain-model.md#ENTITY-y]

## Rules

### RULE-{DOMAIN}-{NNN}: {Rule title}

{Plain-language description of the rule. Be precise. State the invariant
or constraint. Include the "why" if it helps clarify intent.}

**Applies to:** {which actors, components, or contexts}
**References:** [{other-spec}#ID, ...]

#### RULE-{DOMAIN}-{NNN}.S01: {Scenario title — the happy path or key case}
- **Given:** {precondition — system state before the action}
- **When:** {action — what the user or system does}
- **Then:** {expected outcome — observable result}
- **Notes:** {optional — clarifications, not tested directly}

#### RULE-{DOMAIN}-{NNN}.S02: {Another scenario}
- **Given:** ...
- **When:** ...
- **Then:** ...
```

### 4.2 Writing Good Given/When/Then

**Given** describes state, not history. Say "a cart with 3 items" not
"the user has added 3 items to the cart."

**When** describes a single action. If you need multiple steps, either
break into multiple scenarios or reference a UXI flow.

**Then** describes observable outcomes. Be specific:
- BAD: "the user sees an error"
- GOOD: "the system returns HTTP 422 with body `{"error": "email_taken", "message": "This email is already registered"}`"
- GOOD: "the UI displays an inline error below the email field reading 'This email is already registered'"

**Then** may include multiple assertions (use a bulleted sub-list):
```markdown
- **Then:**
  - The order status changes to "confirmed"
  - The user receives a confirmation email
  - The inventory count for each item decreases by the ordered quantity
```

### 4.3 Scenario Categories

Mark scenarios with a category tag in the title for prioritization:

- `[happy]` — the expected, successful path
- `[edge]` — boundary condition or unusual-but-valid input
- `[error]` — invalid input, failed precondition, system error
- `[security]` — authentication, authorization, injection, etc.
- `[performance]` — response time, throughput, concurrency constraints

Example: `#### RULE-AUTH-001.S03: Too short password [error]`

### 4.4 Data Tables

When a rule has many input/output variations, use a data table instead of
separate scenarios:

```markdown
#### RULE-PAY-005.S01: Currency formatting [happy]
- **Given:** a completed order
- **When:** the receipt is generated
- **Then:** amounts are formatted per locale:

| Input Amount | Locale  | Expected Output |
|-------------|---------|-----------------|
| 1234.50     | en-US   | $1,234.50       |
| 1234.50     | de-DE   | 1.234,50 €      |
| 1234.50     | ja-JP   | ¥1,235          |
```

Agent 1 should generate a parameterized test from data tables.

---

## 5. Glossary Format

The glossary defines project-specific terms used across all specs.

```markdown
# Glossary

## TERM-{name}: {Display Name}

**Definition:** {One clear sentence defining the term.}

**Constraints:** {Optional — value ranges, formats, invariants.}

**Examples:**
- {Valid example}
- {Another valid example}

**Anti-examples:**
- {Something that might be confused for this term but is not}

**Related:** [TERM-{other}], [ENTITY-{other}]
```

Anti-examples are important — they prevent Agent 1 from generating tests
based on incorrect assumptions about what a term means.

---

## 6. Domain Model Format

The domain model defines entities, their relationships, and their invariants.

```markdown
# Domain Model

## ENTITY-{name}: {Display Name}

**Description:** {What this entity represents.}

**Attributes:**
| Attribute     | Type        | Required | Constraints              |
|--------------|-------------|----------|--------------------------|
| id           | UUID        | yes      | System-generated         |
| email        | string      | yes      | Valid email, unique       |
| created_at   | datetime    | yes      | Immutable after creation |

**Invariants:**
- {Statement that must always be true, e.g., "An order must have at least one line item"}
- {Another invariant}

**Relationships:**
- Has many: [ENTITY-order]
- Belongs to: [ENTITY-organization]

**Lifecycle States:**
{If the entity has a state machine, define it here:}

```
[created] → [active] → [suspended] → [active]
                     → [deleted]
[active] → [deleted]
```

**Transition Rules:**
- created → active: {condition, e.g., "email verified"}
- active → suspended: {condition}
- suspended → active: {condition}
- Any state → deleted: {condition, e.g., "admin action or user request"}
```

Entity invariants become assertions in integration tests. Lifecycle states
become state-machine tests.

---

## 7. UXI Flow Format

UXI flows describe user journeys through the system.

```markdown
# FLOW-{NAME}-{NNN}: {Flow Title}

## Metadata
- Actor: {who performs this flow — e.g., "unauthenticated user", "admin"}
- Entry Point: {URL or trigger — e.g., "/welcome", "clicks invite link"}
- Success Exit: {where the user ends up on success}
- Failure Exit: {where the user ends up on failure}
- References: [auth.spec.md#RULE-AUTH-001], ...

## Preconditions
- {What must be true before this flow starts}

## Steps

### FLOW-{NAME}-{NNN}.STEP-01: {Step title}
- **Page/Screen:** {URL or screen name}
- **User Action:** {What the user does}
- **System Response:** {What the system does in response}
- **Components:** {UI components involved — optional}
- **Transitions:**
  - On success → STEP-02
  - On error → {describe error state or link to error step}

### FLOW-{NAME}-{NNN}.STEP-02: {Step title}
...

## Error States

### ERR-01: {Error name}
- **Trigger:** {What causes this error}
- **Display:** {What the user sees — exact text if specified in brand/voice}
- **Recovery:** {How the user recovers — link to another step or flow}

## Edge Cases
- {Describe unusual but valid paths through this flow}
```

Agent 1 generates e2e tests from the step sequence and component tests
from individual steps. Error states become dedicated test cases.

---

## 8. API Contract Conventions

### 8.1 OpenAPI Specs

API contracts use standard OpenAPI 3.x format in `specs/api/openapi.yaml`.
Each endpoint should include:
- `operationId` matching the format `API-{METHOD}-{RESOURCE}-{NNN}`
- `x-spec-refs` extension listing related behavior spec IDs
- Complete request/response schemas with examples
- Error response schemas for all documented error codes

```yaml
paths:
  /users:
    post:
      operationId: API-POST-USERS-001
      x-spec-refs:
        - "auth.spec.md#RULE-AUTH-001"
        - "auth.spec.md#RULE-AUTH-002"
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
            examples:
              valid:
                value:
                  email: "user@example.com"
                  password: "SecurePass123"
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '422':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ValidationError'
              examples:
                email_taken:
                  value:
                    error: "email_taken"
                    message: "This email is already registered"
```

### 8.2 Contract Test Generation

Agent 1 uses the OpenAPI spec to generate:
- Request validation tests (required fields, types, constraints)
- Response shape tests (status codes, schema compliance)
- Example-based tests (using the `examples` in the spec)
- Cross-referencing with behavior spec scenarios via `x-spec-refs`

---

## 9. Brand Chapter Conventions

### 9.1 Voice and Tone

```markdown
# Brand Voice & Tone

## Voice Attributes
- {attribute}: {description + example}
  - DO: "{example of correct usage}"
  - DON'T: "{example of incorrect usage}"

## Tone by Context
| Context            | Tone       | Example                          |
|-------------------|------------|----------------------------------|
| Success messages   | Warm       | "Welcome aboard, {name}!"       |
| Error messages     | Helpful    | "That email's already taken..."  |
| System errors      | Reassuring | "Something went wrong. We're..." |

## Terminology Rules
- Always say "{preferred}" not "{deprecated}"
- Never use: {list of forbidden terms}
```

Agent 3 uses this chapter to validate user-facing strings in code.

### 9.2 Visual Identity

```markdown
# Visual Identity

## Color Tokens
| Token         | Value    | Usage                    |
|--------------|----------|--------------------------|
| primary      | #XXXXXX  | Buttons, links           |
| error        | #XXXXXX  | Error states, alerts     |

## Typography
| Role     | Font      | Weight | Size  |
|---------|-----------|--------|-------|
| heading | {font}    | 700    | 24px  |
| body    | {font}    | 400    | 16px  |

## Spacing Scale
{base unit, scale, usage rules}
```

Agent 1 can generate visual regression test baselines from these tokens.
Agent 3 validates that code uses tokens rather than hardcoded values.

---

## 10. Spec Lifecycle

### 10.1 Status Values

| Status       | Meaning                                                  |
|-------------|----------------------------------------------------------|
| `draft`     | Work in progress. Agent 1 may generate tests but marks them `@skip`. |
| `review`    | Awaiting human review. Tests generated but not enforced. |
| `stable`    | Approved. Tests are enforced. Agent 2 must satisfy them. |
| `deprecated`| Being phased out. Tests remain but are marked for future removal. |

### 10.2 Change Protocol

When modifying a spec:
1. Update the `Last Updated` date in metadata
2. If adding new rules: assign the next sequential ID
3. If removing rules: change status to `deprecated`, do not delete
4. If changing a rule's meaning significantly: deprecate the old ID, create a new one
5. Always update cross-references in other specs if entity names or rule IDs change

### 10.3 Deprecation

Deprecated specs and rules:
- Keep the ID forever (never reuse)
- Add a `Deprecated` notice with the date and reason
- Add a `Replaced by` reference if applicable
- Agent 1 marks corresponding tests as `@skip` with a deprecation comment
- After all code references are removed, the test can be deleted in a cleanup pass

---

## 11. Validation Checklist

Before considering a spec complete, verify:

- [ ] Every rule has a unique, correctly formatted ID
- [ ] Every rule has at least one `[happy]` scenario and one `[error]` scenario
- [ ] Every scenario has all three: Given, When, Then
- [ ] Every `Then` is specific and testable (not vague like "works correctly")
- [ ] All domain terms used are defined in the glossary
- [ ] All entity references exist in the domain model
- [ ] All cross-references use the correct file path and ID
- [ ] The status field is set correctly
- [ ] Data tables have at least 3 rows (enough to catch patterns)
- [ ] UXI flows define error states and recovery paths
- [ ] API endpoints have complete request/response schemas with examples
- [ ] Brand-sensitive strings (error messages, UI text) match the voice-and-tone guide

---

## 12. Example: Minimal Complete Spec

```markdown
# Feature: Password Reset

## Metadata
- Domain: AUTH
- Status: stable
- Last Updated: 2026-03-28
- Dependencies: [glossary.md#TERM-session], [domain-model.md#ENTITY-user]

## Context
Allows users to reset their password via email. Referenced by
[flows/password-reset.flow.md#FLOW-PWRESET-001].

## Rules

### RULE-AUTH-010: Reset link expiration
Password reset links expire 30 minutes after generation.
A user may request a new link at any time, which invalidates
all previous links.

**Applies to:** unauthenticated users with a registered email
**References:** [glossary.md#TERM-reset-token]

#### RULE-AUTH-010.S01: Valid reset within window [happy]
- **Given:** a user with email "user@example.com" exists
- **When:** the user requests a password reset and clicks the link within 30 minutes
- **Then:**
  - The system presents the "set new password" form
  - The reset token is marked as "consumed"

#### RULE-AUTH-010.S02: Expired reset link [error]
- **Given:** a user requested a password reset 31 minutes ago
- **When:** the user clicks the reset link
- **Then:**
  - The system returns HTTP 410 Gone
  - The UI displays "This link has expired. Request a new one."

#### RULE-AUTH-010.S03: Second request invalidates first [edge]
- **Given:** a user requested a password reset (link A), then requests again (link B)
- **When:** the user clicks link A
- **Then:**
  - The system returns HTTP 410 Gone
  - Link B remains valid

#### RULE-AUTH-010.S04: Reset for non-existent email [security]
- **Given:** no user with email "nobody@example.com" exists
- **When:** someone requests a password reset for that email
- **Then:**
  - The system responds with the same success message as a valid request
  - No email is sent
  - **Notes:** This prevents email enumeration attacks
```
