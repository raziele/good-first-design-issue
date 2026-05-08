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
