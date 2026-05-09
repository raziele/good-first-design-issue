# CI/CD Doctor Log

Persistent record of CI issues, fixes, and derived rules for this project.

---

## 2026-05-08 — Run #25521350415 (main, post-merge of PR #12)

### Issues Found
- gate-failure: `pre_codegen_red_phase` failed with "Backend generated tests unexpectedly passed pre-codegen" — root cause: agent-1-testgen produced **self-stubbed inert tests** that define helper functions and constants inline (e.g., `classify()` defined inside `test_classification.py`) and never import from the system under test (`app.*`). They pass against any implementation because they assert against their own inline stubs.
- false-negative: frontend red-phase check accepted `vitest exit 1 + "No test files found"` as "failed as expected" — the failure was a misconfigured include glob in `src/frontend/vite.config.ts`, not a real test failure. Any future run with self-stubbed frontend tests would silently pass the gate.
- vitest-config-gap: `src/frontend/vite.config.js` had no `test` block; vitest's default include `**/*.{test,spec}.?(c|m)[jt]s?(x)` is rooted at `src/frontend`, so `tests/frontend/**` was never matched and vitest exited 1 with "No test files found" — which the gate misread as expected red.
- trigger-leak: workflow ran on a CI-only PR (no spec changes) because `.github/workflows/specs-to-code.yml` is in the trigger `paths`. Combined with the testgen defect this produces a cycle of identical inert-test runs.

### Fixes Applied
- `agents/agent-1-testgen/prompt.md`: added explicit Anti-Patterns section forbidding inline SUT implementations; required every test file to import from the SUT (`from app.*` for backend, relative imports of `src/frontend/src/*` for frontend); restated red-phase contract.
- `.github/workflows/specs-to-code.yml`: red-phase step now (1) runs a static SUT-import guard before pytest/vitest, (2) treats `vitest exit 1 + zero collected files` as a gate failure rather than expected red, (3) keeps the existing pytest-collected-zero check.
- `src/frontend/vite.config.js`: added `test.include` covering `../../tests/frontend/**/*.{test,spec}.?(c|m)[jt]s?(x)` and `test.environment: 'jsdom'`. Added `jsdom` to `src/frontend/package.json` devDependencies so component tests can render.

### Structural Gaps Identified
- The testgen prompt described WHAT to test but never specified that tests must exercise production modules. Without that constraint, the model defaults to writing self-contained spec-as-assertions.
- Red-phase gate trusted exit codes alone to distinguish "expected red" from "config bug." Any non-zero exit was treated as success of the gate.
- No upstream guard verified that generated tests reference real modules. The pipeline relied on transitive evidence (post-codegen green) which never ran because the gate blocked first.

### Rules Derived
- Generated tests **must import the SUT**. Static guard required at red-phase, not just at post-codegen.
- Red-phase gates **must validate that something was actually run**, not just that exit code was non-zero. Distinguish: exit 0 → bad (pre-codegen pass), exit 5 / "no tests collected" → config bug (fail loudly), exit 1+ with collected tests + assertions failing → expected red.
- Testgen prompts **must explicitly forbid mirroring production logic in test fixtures.** Stubs belong in `conftest.py` / setup files, not in the test bodies that assert behavior.
- When a vitest `vite.config.*` lives in a sub-app directory but tests live at repo root, **`test.include` must be explicit** — vitest's default is rooted at the config file's directory.

### Follow-up (same day) — diff-scoped red phase

The bucket-level gate ("at least one test in `tests/backend/` failed") is a
greenfield approximation that breaks once `main` carries real passing tests:
an unrelated old failure can satisfy the gate while every newly-generated test
trivially passes. Replaced with **diff-scoped, per-file** semantics:

- `pre_codegen_red_phase` now fetches `origin/main` (`fetch-depth: 0`),
  computes `git diff --name-only --diff-filter=AM origin/main...HEAD --` for
  `tests/backend/test_*.py` and `tests/frontend/**/*.{test,spec}.[cm]?[jt]sx?$`,
  and writes the lists to `$RUNNER_TEMP`.
- The SUT-import guard scans **only those changed files** (existing main content
  is out of scope for this cycle).
- The red-phase verifier runs each changed test file **individually** and
  requires non-zero exit per file. exit 0 = unexpected pass (gate fails), exit 5
  / vitest "No test files found" = config bug (gate fails), any other non-zero =
  expected red (file passes the gate).
- If the diff yields zero changed test files, the gate emits a `::warning::` and
  exits 0 — there is no red to verify and downstream codegen is allowed to
  no-op rather than the pipeline hard-failing.

Updated `agents/agent-1-testgen/prompt.md` to describe these semantics
explicitly, including the consequence that adding tests for already-implemented
rules is a gate failure (delete the redundant test or drive net-new behavior).

---

## 2026-05-08 — Run #25576299769 (main, post-merge of PR #13)

### Issues Found

- gate-failure: 1 of 12 changed test files (`tests/backend/test_api_health.py`)
  passed pre-codegen. The agent generated a contract test that pinned the
  pre-existing `/health` endpoint baked into the FastAPI scaffold since project
  bootstrap. The test imported `from app.main import app` (legitimate SUT
  import), but every assertion was already satisfied. The agent's own docstring
  acknowledged the situation: *"Tests for the /health endpoint (pre-existing —
  baseline contract)."*
- structural-conflict: strict TDD red-phase requires every changed test to
  fail; contract tests for stable scaffold endpoints can never fail without
  removing the scaffold. The two requirements are mutually exclusive without a
  channel for "contract tests."

### Fixes Applied (Option B — path-based exemption + agent scope restriction)

- `pipeline/locks.yaml`: replaced agent-1-testgen `write: ["tests/**"]` with an
  explicit allow-list of subdirectories — `tests/backend/{unit,integration}/**`,
  `tests/frontend/{unit,component,e2e}/**`, plus the manifest, requirements, and
  conftest files. Added `tests/backend/contract/**` and
  `tests/frontend/contract/**` to the deny list. Agent-1 can no longer write
  contract tests at all.
- `scripts/validate_scope.sh`: now reads both `write` and `deny` from
  `locks.yaml` and reports each separately. Also switched from
  `git diff --name-only` (tracked-only) to
  `git ls-files --modified --others --exclude-standard` so brand-new files in
  denied paths are caught (the prior implementation missed untracked files
  because the validator runs before the workflow's `git add`).
- `agents/agent-1-testgen/prompt.md`: rewrote `## Outputs` with the explicit
  allow-list and a hard rule forbidding contract tests; added an anti-pattern
  for pinning baseline scaffold behavior; clarified subdirectory placement
  (flat `tests/backend/test_*.py` is now also a scope violation).
- `.github/workflows/specs-to-code.yml`: `Compute changed test files` step now
  excludes `tests/backend/contract/**` and `tests/frontend/contract/**` from the
  diff lists, so contract tests are exempt from the red-phase gate (defense in
  depth — even if a human pushes a contract test on a feature branch, it won't
  block the pipeline).

### Structural Gaps Identified

- The pre-existing `pipeline/locks.yaml` had no enforcement for the `deny`
  field; only `write` was checked. Any path that wasn't in `write` was simply
  flagged as "outside scope," conflating actively-denied paths with
  unspecified ones.
- The validator missed brand-new (untracked) files because it relied on `git
  diff` semantics, undermining any deny rule for paths the agent could create
  for the first time.
- The role of agent-1 was implicit: it was supposed to write driver tests, not
  contract tests, but no rule said so. The rebuilt prompt and locks now make
  this contract explicit.

### Rules Derived

- Permission models for AI-agent file scopes need both **allow** and **deny**
  enforcement, not just allow. Deny lets you carve out exempt subtrees within
  an otherwise allowed parent.
- Scope validators that run before staging (`git add`) MUST include untracked
  files (`git ls-files --modified --others --exclude-standard`), not just
  tracked diffs.
- TDD red-phase gates on real codebases need a channel for **contract tests**
  that pin pre-existing baseline behavior. Either exempt them by path, by
  marker, or by ownership (humans only). This project chose ownership +
  path: contract tests live under `tests/**/contract/**`, owned by humans, and
  are exempt from the red-phase diff scope.

---

## 2026-05-09 — Run #25597958969 (main, post-merge of PR #14)

### Issues Found

- gate-failure: `Validate file scope` step in `agent_1_testgen` rejected the
  run with `agent-1-testgen modified files outside its allowed write scope:
  skills-lock.json`. Agent-1 itself produced clean output — 14 well-organized
  test files under `tests/backend/{unit,integration}/` and
  `tests/frontend/{unit,component,e2e}/`, all importing the SUT, all under
  the new explicit allow-list. The only violation was `skills-lock.json` at
  repo root, which is created by the preceding `Install testgen skills`
  step (`npx skills@latest add ...`), not by the agent.
- structural: PR #14's switch from `git diff --name-only` (tracked-only) to
  `git ls-files --modified --others --exclude-standard` (also untracked) was
  the correct fix for catching new files in denied paths, but it newly
  surfaced legitimate CI infrastructure artifacts. `skills-lock.json` is
  ephemeral state regenerated by the skill installer on every CI run; it
  should never be tracked or attributed to any agent.

### Fixes Applied

- `.gitignore`: added `skills-lock.json` next to the existing `.agents/skills/`
  and `.cursor/skills/` entries, since it's the same class of artifact (CI
  infrastructure produced by `npx skills@latest add`, not source). With it
  gitignored, `--exclude-standard` will hide it from the validator without
  any logic change.

### Structural Gaps Identified

- `.gitignore` only listed two of the three skill-installer artifacts. The
  rule "skill-installer outputs are ignored" was applied to the directories
  but not to the lockfile, even though both are produced by the same `npx`
  command and share identical lifecycle properties.
- The validator now correctly assumes "every untracked file in the worktree
  was produced by this agent." For that assumption to hold, every CI step
  that runs *before* the agent in the same job must either write outside the
  worktree or write to gitignored paths.

### Rules Derived

- When a CI step in the same job as the agent produces files in the
  worktree, those files MUST be gitignored. The validator's "untracked =
  agent's writes" assumption only holds if non-agent writes are invisible
  to git's untracked listing.
- When introducing a new pre-agent step that writes to the repo, audit
  `.gitignore` immediately. If the artifact has no source-of-truth value,
  ignore it.
