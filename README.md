# AI-First TDD Monorepo

**Specs are the source of truth. Tests are the contract. Code is the output.**

## Architecture

```
Human writes specs -> Agent 1 generates tests -> Agent 2 writes code -> Agent 3 reviews
```

## Structure

| Directory | Owner | Purpose |
|-----------|-------|---------|
| `specs/` | Human | Behavior specs, domain knowledge, UXI flows, API contracts |
| `tests/` | Agent 1 | Generated tests — locked from Agent 2 |
| `src/` | Agent 2 | Implementation code |
| `agents/` | Human | Agent prompts and configuration |
| `pipeline/` | CI | Orchestration, triggers, reports |
| `tools/` | Shared | Spec linter, diff detector, coverage mapper |

## Getting Started

1. Write specs in `specs/behavior/` using the format in `specs/spec-schema.md`
2. Define domain terms in `specs/chapters/glossary.md`
3. Run the pipeline: `python pipeline/orchestrator.py`

## Agent Workflow

1. **Agent 1 (Test Generator)** reads specs, produces tests in `tests/`
2. **Agent 2 (Code Generator)** reads tests (contract) + specs (context), writes code in `src/`
3. **Agent 3 (Reviewer)** validates changes against quality gates, produces reports
