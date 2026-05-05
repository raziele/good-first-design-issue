# Feature: Claiming an Issue

## Context
- References: [glossary.md#claim], [glossary.md#claim-comment], [domain-model.md#issue]
- UXI Flow: [flows/claim-issue.flow.md]

## Rules

### RULE-CLM-001: Claim action offers two options
When a user initiates a claim, they are offered two paths: (1) redirect to GitHub with a pre-filled comment, or (2) copy the comment to clipboard.

#### Scenario: User chooses to go to GitHub
- Given: A user is viewing an issue detail
- When: The user clicks "Claim This Task" and selects "Go to GitHub"
- Then: The user is redirected to the GitHub issue comment form
- And: The comment field is pre-filled with an AI-generated claim comment

#### Scenario: User chooses to copy comment
- Given: A user is viewing an issue detail
- When: The user clicks "Claim This Task" and selects "Copy comment"
- Then: The AI-generated claim comment is copied to clipboard
- And: A confirmation message is shown

---

### RULE-CLM-002: Claim comment is AI-generated
The claim comment is contextually generated based on the issue content, not a fixed template.

#### Scenario: Comment reflects issue context
- Given: An issue about "mobile onboarding redesign"
- When: The claim comment is generated
- Then: The comment mentions design/UX intent
- And: The comment may reference the specific task type (e.g., "I'll work on the onboarding flow")

---

### RULE-CLM-003: No local claim tracking
Level8 does not track claims in its database. Claim status is determined by refreshing issue data from GitHub.

#### Scenario: Claim does not update local database
- Given: A user claims an issue via Level8
- When: The claim action completes
- Then: No local database record is created for this claim
- And: The issue's `is_claimed` status will update on next ETL refresh

---

### RULE-CLM-004: Multiple users can claim same issue
Level8 does not prevent multiple users from attempting to claim the same issue.

#### Scenario: Second user can claim already-attempted issue
- Given: User A has claimed an issue via Level8
- And: User B views the same issue
- When: User B clicks "Claim This Task"
- Then: User B is offered the same claim options
- And: No warning or block is shown
