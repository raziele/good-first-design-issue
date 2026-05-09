# Plan: Stub-first TDD pipeline (Alt A spine)

**Status:** Draft plan — not implemented until merged as adopted work.  
**Related:** `docs/ci-pipeline-definition-of-done-alternatives.html` (analysis + visuals §7).  
**Goal:** Give `agent-2-codegen` a **concrete starting state** (imports resolve, behavior stubbed) and a **concrete target** (no stub markers, full suite green), aligning CI with Beck-style *make it compile → make it run → refactor* and reducing red-phase log heuristics.

---

## Resolved decisions (stakeholder Q&A)

Captured so implementation does not re-litigate defaults.

| Topic | Decision | Notes |
|--------|----------|--------|
| **Who commits stubs** | **`agent-1-testgen[bot]`** (same identity as tests) | Stubs land in a follow-up commit after tests on the feature branch, or in an extended agent-1 job — workflow design must keep scope validator attribution consistent with `PRE_SNAPSHOT`. |
| **Stub write scope** | **Undecided — Phase 0 checkpoint** | **Default in this plan:** `src/backend/app/**` only. Widen to broader `src/backend/**` only after an explicit Phase 0 decision (e.g. tests that import outside `app.`). |
| **Phase 1 class support** | **Functions MVP** | Generator supports **functions** first. Tests that require **class instantiation / methods** fail stub-gen (or CI) with a **clear, documented error** until Phase 1b extends the generator. |
| **Post-codegen check** | **Stricter: ban `NotImplementedError` under `app/`** | User chose stricter than marker-only. **Caveat:** legitimate production `NotImplementedError` in `app/` will fail CI — avoid or narrow path (e.g. only files that ever contained stub marker) if that appears in real code. |
| **Frontend (Phase 6)** | **Deferred indefinitely** | Backend-only stub pipeline is acceptable long-term; frontend parity only if explicitly requested later. |

---

## 1. Problem statement

- Today, driver tests may import `app.*` before modules exist. Collection-time failures are **legitimate TDD red** but are hard to distinguish from **misconfiguration** (plugins, conftest, etc.) when the gate is built from exit codes and `grep`.
- `agent-2-codegen` has no uniform first step: sometimes it must **create files**, sometimes **edit** them — the optimization target is fuzzy.
- Post-codegen tests are the only structurally clean DoD; earlier stages approximate intent.

## 2. Target architecture (summary)

1. After tests land on the feature branch, a **deterministic stub generator** creates/updates `src/backend/app/*.py` so every SUT import from changed tests resolves. Stubs raise a **single grep-able marker** (e.g. `NotImplementedError("SUT stub — implement in agent-2-codegen")`).
2. **Red phase** verifies changed driver tests **run** and fail at **assertions** (pytest summary shows failures), not at import/collection ambiguity.
3. **Agent 2** replaces stubs with real implementations until local/CI green.
4. **Post-codegen** runs full suite and **fails if stubs remain**: **resolved** — scan for **`NotImplementedError` under `app/`** (strict); keep **stub marker** check for clearer errors.
5. **Frontend** stub parity — **deferred indefinitely** (not part of this initiative unless re-scoped).

Contract tests under `tests/**/contract/**` remain **exempt** from red-phase (existing path policy = thin Alt E).

---

## 3. Out of scope (this plan)

- Replacing `agent-3-review` or PR automation.
- Heavy OpenAPI/Pact **Alt D** for external services (optional follow-up).
- Rewriting agent prompts end-to-end beyond what stub flow requires.
- **Frontend stub parity** (former Phase 6) — deferred indefinitely unless explicitly re-scoped.

---

## 4. Phases & deliverables

### Phase 0 — Preconditions (no code or minimal)

| Task | Done when |
|------|-----------|
| Confirm backend package layout | `src/backend/app/` (or documented canonical package) matches test imports `from app.…` |
| **Decide stub generator write roots** | **Default:** `src/backend/app/**` only. If tests need stubs elsewhere under `src/backend/`, document allow-list and update generator + locks in the same PR. |
| Agree stub marker string | Single stable substring for CI `grep` (e.g. `SUT stub — implement in agent-2-codegen`) |
| Agree who commits stubs | **Resolved:** **`agent-1-testgen[bot]`** — stub commit is part of the testgen “wave” (same bot, sequential commit(s) on the feature branch before red-phase). |

### Phase 1 — Stub generator (backend)

| Task | Done when |
|------|-----------|
| Add `scripts/generate_sut_stubs.py` (or `uv run` module under `scripts/`) | Idempotent: re-run does not duplicate defs; only touches stub files / new modules under allow-listed roots |
| Parse test files | Collect `from app.X import a, b` and `import app.X`; resolve symbols per file |
| Emit stubs | **MVP:** **functions only** — for each missing module/symbol that is imported as a callable, emit `def name(*args, **kwargs): raise NotImplementedError("…marker…")`. **Class-heavy tests** (instantiation, methods) → **fail stub generation** with explicit message until Phase 1b. |
| Unit-test the generator | Small fixtures: sample test file → expected stub output on disk or golden file |
| Document limitations | Known limitation from scope-validator doc: modifying same untracked file — stubs should be **committed** so post-state is tracked |

**Acceptance criteria**

- Running the script on a branch that only has tests (no `app.foo`) produces `app/foo.py` (or correct path) such that `python -m pytest <that test file>` progresses past **import** to **assertion failure** (or skip if no assertions — should not happen for driver tests).
- No network; no LLM.

### Phase 2 — Wire into CI (`specs-to-code.yml`)

| Task | Done when |
|------|-----------|
| New job or step **after** agent-1 commits tests, **before** `pre_codegen_red_phase` | Checks out feature branch; installs minimal deps (stdlib + `pyyaml` if needed for locks only — generator should avoid extra deps if possible); runs stub script |
| Commit stubs | `git add` under agreed write root (default `src/backend/app/**`); commit as **`agent-1-testgen[bot]`**; push to feature branch. May be second commit in same job after tests or a chained step — must not break scope rules for agent-1. |
| Scope validation | Stubs touch **`src/**`**: today agent-1 is **denied** `src/**` in `locks.yaml`. **Implementation must either:** (a) run stub generation + commit in a **separate job** with its own bot/permissions, or (b) **extend locks + prompts** so agent-1 is allowed only `src/backend/app/**` for stub output, or (c) use a **non-agent** workflow step with `contents: write` that is exempt from per-agent scope (document choice in Decision log). |

**Acceptance criteria**

- A workflow run on `main` with new tests results in stub files on the feature branch before red-phase.
- No duplicate commits on re-run if nothing changed (idempotent git state).

### Phase 3 — Simplify red-phase (backend)

| Task | Done when |
|------|-----------|
| Replace multi-branch “collection ImportError vs config” logic where obsolete | For backend driver tests: require pytest **session summary** and **≥1 failed test** (or equivalent “failed” count in summary — document exact `grep`/parser) |
| Keep guards | Static SUT-import guard unchanged; contract path exclusions unchanged |
| Vitest branch | Unchanged in this phase unless parity desired later |

**Acceptance criteria**

- Synthetic cases: (1) stub present, assertion fails → gate passes. (2) plugin crash, no summary → gate fails. (3) conftest error → gate fails. (4) test passes pre-codegen → gate fails.

### Phase 4 — Post-codegen enforcement

| Task | Done when |
|------|-----------|
| Scan `src/backend/app/` (or agreed app package root) | **Resolved:** fail if **any** `NotImplementedError` appears in production modules under `app/` (user-selected strict mode). Prefer `rg`/AST to reduce false matches in strings/comments. |
| Also recommended | Keep checking for **stub marker substring** for clearer error messages when stubs were not replaced. |
| False-positive policy | If real code must raise `NotImplementedError`, narrow the scan (e.g. only files touched in the cycle) or switch to marker-only — document in Decision log. |

**Acceptance criteria**

- If agent-2 leaves a stub (marker or `NotImplementedError` in `app/`), post-codegen fails with clear message.

### Phase 5 — Prompt & lock updates

| Task | Done when |
|------|-----------|
| `agents/agent-2-codegen/prompt.md` | States: stubs may exist; replace stub marker with real behavior; do not remove tests |
| `agents/agent-1-testgen/prompt.md` | Optional: mention stubs will be generated — tests must import `app.*` consistently |
| `pipeline/locks.yaml` / validator | Any new commit identity for stub job must match allowed paths |

### Phase 6 — Frontend (deferred indefinitely)

Not in scope until explicitly re-requested. If revived: design TS stub strategy, Vitest import resolution, red-phase parity.

**Previous text:** defer until Phase 1–4 stable — **superseded** by stakeholder choice to defer frontend work without a fixed date.

---

## 5. Risk register

| Risk | Mitigation |
|------|------------|
| Stubs wrong shape (class vs function) | **MVP:** functions only; class tests blocked with clear error; Phase 1b extends generator |
| **agent-1 cannot commit `src/**` today** | Resolve in Phase 2: separate job, lock change for narrow path, or non-agent step — **must be decided before coding** |
| Agent-2 deletes stubs instead of implementing | Post-codegen scan; review prompt |
| Duplicate module layout vs human code | Stubs only under agreed tree; codegen allowed to refactor **within** `src/**` after green |
| **`NotImplementedError` banned in `app/`** | User chose strict check — **false positive** if prod uses `NotImplementedError`; narrow scan or relax to marker-only |
| Scope validator attributes stub commit to wrong agent | Pre-snapshot per job; document bot vs non-agent stub step |

---

## 6. Verification checklist (before closing initiative)

- [ ] One full `Specs to Code` run on `main` with new specs: stubs appear, red-phase passes, codegen passes, post-codegen passes.
- [ ] Deliberately break stub generator input in a throwaway branch: CI fails fast with readable error.
- [ ] Contract tests still do not block red-phase.
- [ ] `docs/ci-pipeline-definition-of-done-alternatives.html` cross-linked from this plan (already related).

---

## 7. Decision log (fill in when executing)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Stubs committed by **agent-1-testgen[bot]**; write scope **TBD** in Phase 0 with default **`src/backend/app/**`**; Phase 1 **functions MVP**; post-codegen **ban `NotImplementedError` in `app/`**; **frontend deferred indefinitely** | Stakeholder Q&A — removes ambiguity for implementers; note `locks.yaml` conflict for agent-1 writing `src/**` must be resolved in Phase 2. |
| 2026-05-09 | **Implemented:** stub generator + meta unit tests; stub commit as **second step in `agent_1_testgen` job** (avoids skipped `needs` job); red-phase requires **summary + N failed** with ImportError fallback; post-codegen **marker grep + AST check** for `NotImplementedError` | Locks conflict resolved by **not** attributing stub files to the LLM scope check — deterministic script runs after `validate_scope` and after the test commit; same bot identity for git author. |

---

## 8. References

- Internal: `docs/ci-pipeline-definition-of-done-alternatives.html` — §7 visuals.
- Beck, *Test-Driven Development By Example* — compile/stub/Fake It cycle (consult via CandleKeep `ck` in library).
- Prior CI doctor log entries on red-phase and scope validation (`.cursor/ci-doctor-log.md`).
