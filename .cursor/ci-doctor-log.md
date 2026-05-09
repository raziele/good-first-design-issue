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

---

## 2026-05-09 — Run #25598513599 (main, workflow_dispatch)

### Issues Found

- false-green / silent-gate-bypass: `pre_codegen_red_phase` reported
  `OK: failed as expected (exit 1)` for **every** changed backend test file
  (`test_classification.py`, `test_etl.py`, `test_issues.py`, `test_search.py`).
  No tests actually ran. Root cause: agent-1-testgen added
  `pytest-freezegun==0.4.2` to `tests/requirements.txt`. That package was
  last released in 2019 and `pytest_freezegun.py` line 5 does
  `from distutils.version import LooseVersion`. Python 3.12 removed
  `distutils` (PEP 632), so pytest crashed inside `parse(args)` →
  `load_setuptools_entrypoints("pytest11")` before any test was collected.
  Pytest exited 1 → the gate's `case "$rc"` fell into `*)` →
  `OK: $f failed as expected`. The 2026-05-08 rule "red-phase gates must
  validate that something was actually run" was bypassed by a different
  failure mode (plugin-load crash vs. zero collection). Codegen then ran
  on a hollow red signal. The pipeline only got caught downstream by
  Issue #2 below; without that, agent-2 would have committed code that
  was never actually tested against the new tests.
- scope-violation / structural-gap (blocker): `agent_2_codegen` →
  `Validate file scope` failed with
  `agent-2-codegen modified files outside its allowed write scope:
  .vite/vitest/results.json`. Agent-2's actual outputs were correct
  (45 backend + 66 frontend tests passing in its local run). The
  violation came from vitest writing its results cache into
  `src/frontend/.vite/vitest/results.json` when agent-2 ran tests as
  part of its own self-verification. Same class as PR #14
  `skills-lock.json`: a CI-tooling artifact that the validator's
  `git ls-files --modified --others --exclude-standard` correctly
  surfaces, but which is not actually agent-attributable. The
  cross-cutting rule from 2026-05-09a was applied narrowly only to
  `skills-lock.json` and missed every other tool that writes to the
  worktree.
- deprecation (24-day fuse): every workflow used Node-20 actions
  (`actions/checkout@v4`, `actions/setup-node@v4`, `actions/setup-python@v5`,
  `actions/upload-artifact@v4`). GitHub will force these to run on Node 24
  starting June 2, 2026.

### Fixes Applied

- `.github/workflows/specs-to-code.yml` — "Verify red phase" backend branch
  now `tee`s pytest output to a tempfile and, on non-zero non-5 exit,
  requires a pytest summary line (`^=+ .* in [0-9]+(\.[0-9]+)?s`) in the
  output. Absence of the summary indicates pytest never finished a run
  (plugin-load crash, conftest import error, internal error) and is now
  treated as a config bug — same severity as exit 5. The previous
  exit-code-only check would let any pre-collection crash slip through
  as "expected red."
- `.gitignore` — added `.vite/` to ignore vitest's cache directory. With
  this, the validator's "untracked = agent's writes" assumption holds
  again whenever agent-2 (or anything else) runs vitest in its job.
- `agents/agent-1-testgen/prompt.md` — added a hard rule to the "Test
  dependencies" section: packages must be maintained for Python 3.12+.
  Specifically forbids `pytest-freezegun` and names `pytest-freezer` or
  direct `freezegun.freeze_time` as the maintained alternatives. Also
  forbids any pytest plugin un-released for >2 years that imports
  removed-in-3.12 stdlib modules (`distutils`, `imp`, `asynchat`,
  `asyncore`, `smtpd`).
- All 4 workflow files — bumped to Node-24-native action versions:
  `actions/checkout@v5`, `actions/setup-node@v6`, `actions/setup-python@v6`,
  `actions/upload-artifact@v6`. Done now rather than waiting for the
  forced cutover, since the runtime swap mid-cycle could mask any
  action-level breakage as a pipeline regression.

### Structural Gaps Identified

- The red-phase gate's exit-code switch had a third silent class of
  failure beyond "exit 0 = pass" and "exit 5 = no collection": pytest
  exiting non-zero **before** running any test. The 2026-05-08 fix
  closed the exit-5 hole but assumed all other non-zero exits meant
  "tests ran and at least one failed." That assumption is wrong for
  any failure during `parse(args)` (plugin loading, option parsing,
  `INTERNALERROR>`). The proper invariant is: "the gate only accepts
  red if pytest produced evidence of having run a test session."
- The cross-cutting rule from 2026-05-09a (gitignore CI tool outputs)
  was applied only to the immediate offender. The pattern "every
  CI-step or local-tool write to the worktree must be gitignored" was
  not enforced as a project-wide invariant — vitest's `.vite/` was
  the next instance, and there will be more (e.g. coverage reports,
  cypress screenshots, playwright traces if added later).
- Agent-2's prompt likely tells it to "verify locally before declaring
  done." Doing so inside the same job as scope validation creates an
  artifact-leakage surface for any tool that writes outside
  `node_modules/`. Future option: either run agent-2's verification in
  a sandboxed temp dir, or run it in a separate job after scope
  validation.

### Rules Derived

- Red-phase gates **must require evidence of a test session**, not just
  a non-zero exit code. For pytest: parse output for the summary line
  `^=+ .* in N.NNs`. For vitest: parse for the test results table or a
  `Tests N passed | N failed` summary. Exit-code-only logic is still
  fundamentally exploitable.
- Maintained-package guard belongs in the testgen prompt, but the
  durable defense is the gate. Prompt-level "don't use abandoned
  packages" rules degrade over time; a gate that requires actual
  test execution catches every future variant of the same class
  (broken plugin, broken conftest, broken assertion-rewrite).
- For every CI tool that runs in any agent's job, **audit `.gitignore`
  for its scratch artifacts before merging the workflow change**.
  The current known list: `.cursor/skills/`, `.agents/skills/`,
  `skills-lock.json`, `.vite/`. Coverage outputs (`htmlcov/`, `.coverage`,
  `coverage.xml`), playwright (`test-results/`, `playwright-report/`),
  and pytest cache (`.pytest_cache/`) are likely future additions.
- When a GitHub Actions runtime deprecation has a date attached
  (e.g. Node 20 → Node 24 force on 2026-06-02), bump action versions
  on a non-feature day **before** the cutoff. A forced runtime swap
  during an unrelated agent run will look like the agent broke the
  pipeline.

---

## 2026-05-09b — Run #25598513599 (revisit, structural fix)

### Re-evaluation

The patch from the previous entry — `gitignore .vite/` — fixes the
immediate symptom but does not address the structural issue that
caused three consecutive runs to fail at scope validation for three
different non-agent tools (`skills-lock.json`, `.vite/vitest/results.json`,
and the next inevitable mole). The validator's invariant —
"`git ls-files --modified --others --exclude-standard` returns the
agent's writes" — is only true when every CI step before the agent in
the same job either writes outside the worktree or writes to gitignored
paths. That maintenance burden has failed every time it's been
tested; relying on it indefinitely is a known-bad design.

Inventory of pre-agent-step writers in the current pipeline:

- `npx skills@latest add` → `skills-lock.json` (now gitignored),
  `.cursor/skills/`, `.agents/skills/`
- `npm install` (in `src/frontend`) → `node_modules/` (gitignored) and
  potentially `package-lock.json` (NOT gitignored — this is the next
  latent failure)
- Agent-2's self-verification per its own prompt: `pytest`
  (`.pytest_cache/`, `__pycache__/`, optionally `.coverage`) and
  `vitest` (`.vite/`, optionally `coverage/`)
- Future plausible additions: playwright, cypress, eslint cache,
  tsbuildinfo, …

### Fixes Applied

- `scripts/validate_scope.sh`: when `$PRE_SNAPSHOT` is set to a path
  containing the same `git ls-files --modified --others
  --exclude-standard` output captured before the agent ran, the
  validator now subtracts that set from the post-agent set via `comm
  -23`. Whatever existed in the worktree before the agent — regardless
  of which tool put it there — is excluded from the agent's
  attribution. When the env var is unset, falls back to the legacy
  behavior with a `::warning::` so this script remains
  backward-compatible during rollout.
- `.github/workflows/specs-to-code.yml`: added a `Snapshot worktree
  (pre-agent)` step before each of `agent_1_testgen`, `agent_2_codegen`,
  and `agent_3_review` invocations. Each step writes the snapshot to
  `$RUNNER_TEMP/worktree-pre-agent-N.txt` and exposes the path via
  `steps.pre_snapshot.outputs.path`. The corresponding `Validate file
  scope` step now passes that path as the `PRE_SNAPSHOT` env var.
- `.github/workflows/pr-approved-docgen.yml`: same pattern for
  `agent_4_docgen`, even though that job has fewer pollution sources
  today — consistency now prevents the next contributor from
  introducing one without thinking about scope.
- `.gitignore` retained its `.vite/`, `skills-lock.json`,
  `.cursor/skills/`, `.agents/skills/` entries as belt-and-suspenders.
  Those entries are no longer required for scope validation to work,
  but they keep the validator honest if a future contributor adds a
  new agent job and forgets the pre-snapshot step (in which case the
  legacy fallback kicks in with a warning).

### Structural Gaps Identified

- The original validator conflated "what's in the worktree right now"
  with "what the agent wrote." That conflation is the actual bug; the
  three `.gitignore` patches were treating its symptom.
- "Audit `.gitignore` for every CI tool" is a project-wide invariant
  that depends on humans remembering. Three consecutive failures
  proved this won't scale — the invariant needs to be embedded in the
  tooling, not in human discipline.
- `package-lock.json` was a latent next failure: today's
  frontend has no committed lockfile, so `npm install` would create one
  in agent-2's job and the validator would have flagged it as soon as
  `.vite/` was fixed. The structural fix closes that case without
  requiring it to fail first.

### Rules Derived

- **Validators that attribute file changes to an actor must use a
  pre/post snapshot, not a single post-state observation.** "Untracked
  files in the worktree right now" is not a sound proxy for "files this
  actor wrote" when other actors share the same workspace before or
  during the run.
- **For every new agent job, add the pre-snapshot step in the same PR
  as the agent invocation.** Co-locating these in one diff makes the
  pattern self-enforcing — reviewers see them together.
- **Keep cheap defense in depth.** Gitignoring tool outputs (`.vite/`,
  `skills-lock.json`, etc.) costs nothing and prevents the legacy
  fallback from generating noise if the pre-snapshot step is ever
  omitted. Don't strip these entries even after the structural fix
  lands.
- **The `::warning::` in the validator's legacy path is the canary.**
  If a future CI run logs "PRE_SNAPSHOT not set," that's the signal
  that an agent job was added without the snapshot step. Watch for it
  in the next few runs.

---

## 2026-05-09c — Run #25606306491 (main, post-merge of PR #16) — self-inflicted regression

### Issues Found

- regression / false-positive: The hardened red-phase gate from PR #16
  (2026-05-09b) rejected the canonical TDD red signal as a config bug.
  All 5 backend test files generated by agent-1 (`test_claim`,
  `test_classification`, `test_etl`, `test_issues`, `test_search`)
  imported `from app.<module>` per the SUT-import guard. None of those
  modules existed yet — that is literally what `agent_2_codegen` is
  scheduled to write next. pytest failed at collection time with exit
  2 and `ImportError while importing test module … / ModuleNotFoundError:
  No module named 'app.X'`, emitting no summary line. The new gate's
  logic was: "non-zero exit + no summary line ⇒ config bug." It rejected
  every file. Codegen never ran. Pipeline halted.
- root cause: my hardening from PR #16 conflated two distinct
  no-summary-line cases:
  1. plugin-load / conftest / internal pytest crash before any test
     could be collected (the `pytest-freezegun` case it was designed
     to catch — exit 1, no test module ever named in output);
  2. legitimate collection-time `ImportError` on the SUT during TDD red
     phase (today's case — exit 2, the test module IS named in output,
     and the missing module is `app.X`).
  Both produce non-zero exit with no summary line; the hardening
  treated them identically. The freezegun case should fail the gate;
  the SUT-not-yet-implemented case is the entire point of red phase
  and must pass.

### Fixes Applied

- `.github/workflows/specs-to-code.yml`, backend `Verify red phase`
  branch — extended the "expected red" criteria to a disjunction:
  - **Path A (test session ran):** final summary line
    `^=+ .* in [0-9]+(\.[0-9]+)?s` is present.
  - **Path B (collection-time SUT import failure):** the log contains
    BOTH `ImportError while importing test module` AND
    `ModuleNotFoundError: No module named 'app.` (or
    `No module named app.` without quotes — pytest's formatting
    varies). The conjunction is specific: plugin-load crashes name
    `_pytest/...` or `conftest`, not the test module; non-SUT import
    errors miss the second clause. The SUT-import guard upstream
    already required every backend test to import `from app.`, so a
    Path-B match is genuinely "the SUT module hasn't been generated
    yet."

  Anything else with non-zero non-5 exit is rejected as a config bug
  (plugin/conftest/internal/non-SUT-import error).
- Frontend gate unchanged — vitest's behavior on missing-SUT imports
  is to emit `Test Files  1 failed (1)` with exit 1 (handled
  correctly by the existing logic).

### Structural Gaps Identified

- The 2026-05-09b rule "red-phase gates must require evidence of a
  test session" was correct but incomplete: in TDD, "evidence of a
  test session" must include "evidence of a deliberate collection-time
  failure on the SUT," because that's a designed red-phase outcome,
  not a malfunction. The previous formulation only contemplated
  "tests ran" as the success path.
- Each tightening of the gate over the last week has shipped with
  high confidence and proved one case too narrow. The shape of the
  gate — heuristic pattern-matching against pytest's exit codes and
  stdout — has more surface area than I keep budgeting for. Worth
  treating as a sign that this approach is approaching its limits.

### Rules Derived

- **Red-phase gate "expected red" is a disjunction, not a single
  invariant.** At minimum it must accept (a) a test session that
  ran and produced failures, AND (b) a collection-time
  `ImportError` whose missing module matches the SUT namespace
  (`app.` for backend in this repo). Add new disjuncts only with a
  matching specificity test (something distinguishing them from
  config bugs).
- **Pattern heuristics decay under load.** Every time the red-phase
  gate has been "hardened" this week, the next failure mode bypassed
  it. Before adding the next disjunct, consider switching to a
  structurally-stronger signal: e.g., `pytest --collect-only` to
  enumerate intended tests with a reason for any non-collection,
  then explicit categorization rather than stdout grep. Filed as a
  follow-up — not part of this hotfix.
- **Always trace-verify a hardened gate against EVERY case it's
  supposed to discriminate, including the legitimate cases.** I
  trace-verified the freezegun-style failure but not the
  SUT-not-yet-implemented case, even though that's the *normal*
  state of the pipeline pre-codegen. A complete trace matrix
  would have caught this in PR #16 review.
