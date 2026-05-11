## Learned User Preferences

- DuckDB queries must use `-readonly` flag
- Run `date` command before executing bash scripts
- Documentation goes under `docs/`; specs/plans go under `docs/specs`
- ETL must be runnable from the `etl/` directory (cd etl && uv run etl)
- Use uv for Python project management
- Prefer objective, candid feedback over agreeableness
- Verify repo state before writing CI commands — check lockfiles, test scripts, and paths before referencing them
- When fixing CI patterns, audit ALL jobs for the same issue — don't scope fixes without a cross-job consistency pass

## Learned Workspace Facts

- Level8 is an AI-first TDD project; specs are the source of truth
- ETL code in `etl/` uses DuckDB (`level8.duckdb`) and `gh` CLI for GitHub API
- Default model name is `composer-2`
- GitHub Search API caps at 1000 results per query; ETL uses date-range bisection
- Railway: deploy via `railway deploy` (no extra flags), Railpack build conventions, workflow triggers only for `agent/feature-*` branches
- Frontend: Vite + React in `src/frontend/`; Backend: FastAPI in `src/backend/` with `/health` endpoint
- DuckDB requires `pytz` at runtime for timezone support
- ETL modes: `--reset` (180 days back, `created:>=`) and default upsert (1 day back, `updated:>=`)
- Specs-to-code workflow uses the canonical TDD skill path under `skills/engineering/tdd`
- Specs-to-code red-phase gate is diff-scoped against `origin/main` (checkout needs `fetch-depth: 0`) and runs only newly added/modified test files per-file (not bucket-level); tests must import the SUT (`from app.<module>` backend / relative `src/frontend/src/*` frontend), self-stubbed inline reimplementations break the gate, and `vitest "No test files found"` / `pytest exit 5` / a missing pytest summary line `^=+ .* in N.NNs` (plugin-load crash) are config bugs, not expected red
- Never pass unbounded shell expansion (e.g., git diff output) as a CLI argument — pipe large data through temp files (Linux ARG_MAX ~2MB)
- In CI, avoid `continue-on-error: true` on dep-install steps — it masks upstream failures and creates false-green results downstream
- Frontend at `src/frontend/` has no committed `package-lock.json` (use `npm install`, not `npm ci`); backend test deps live in `tests/requirements.txt` (within agent-1-testgen's write scope, auto-staged by `git add tests/`)
- `.cursor/skills/` and `skills-lock.json` are gitignored — ephemeral outputs of `npx skills@latest add`, installed fresh per CI job
- Per-agent write/deny scopes live in `pipeline/locks.yaml` and are enforced by `scripts/validate_scope.sh`; `agent-1-testgen` writes only under `tests/{backend,frontend}/{unit,integration,e2e,component}/**` (plus `tests/manifest.json` and `tests/requirements.txt`) and is denied `tests/**/contract/**` and `src/**`
- CI scope validator uses a pre-agent worktree snapshot (`PRE_SNAPSHOT` env var, captured by a `Snapshot worktree (pre-agent)` step before each agent runs) to attribute file changes — replaces the fragile "untracked == agent wrote it" invariant and tolerates artifacts left by earlier CI steps (vitest cache, npm/pip leftovers)
