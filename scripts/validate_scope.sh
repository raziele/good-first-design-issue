#!/usr/bin/env bash
# Validate that an agent only modified files within its allowed write paths.
# Usage: scripts/validate_scope.sh <agent-name>
#
# Reads allowed write paths from pipeline/locks.yaml and checks git diff.

set -euo pipefail

AGENT_NAME="${1:?Usage: validate_scope.sh <agent-name>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Extract allowed write paths and deny paths for this agent from locks.yaml.
# Converts glob patterns like "src/**" to regex prefixes like "^src/".
PATTERNS=$(python3 -c "
import yaml
with open('$REPO_ROOT/pipeline/locks.yaml') as f:
    locks = yaml.safe_load(f)
perms = locks.get('permissions', {}).get('$AGENT_NAME', {})
def to_regex(p):
    if p.endswith('/**'):
        return '^' + p[:-3] + '/'
    return '^' + p + '\$'
print('ALLOWED')
for p in perms.get('write', []):
    print(to_regex(p))
print('DENY')
for p in perms.get('deny', []):
    print(to_regex(p))
print('IGNORE')
for p in perms.get('ignore_for_attribution', []):
    print(p)
")

ALLOWED=$(echo "$PATTERNS" | awk '/^ALLOWED$/{flag=1;next}/^DENY$/{flag=0}flag')
DENY=$(echo "$PATTERNS"   | awk '/^DENY$/{flag=1;next}/^IGNORE$/{flag=0}flag')
IGNORE=$(echo "$PATTERNS" | awk '/^IGNORE$/{flag=1;next}flag')

if [ -z "$ALLOWED" ]; then
    echo "No write permissions defined for $AGENT_NAME — skipping scope check"
    exit 0
fi

# Compute the file set attributable to the agent.
#
# The naive approach — "everything `git ls-files --modified --others
# --exclude-standard` returns is the agent's writes" — is fragile because the
# CI job runs other tools before the agent (npm install, npx skills, vitest,
# pytest, …). Each of those can leave untracked files in the worktree, which
# this validator would then misattribute to the agent unless every one of those
# tool outputs is gitignored. That maintenance has failed three runs in a row
# (skills-lock.json, .vite/, …).
#
# When $PRE_SNAPSHOT points to a file containing the same `git ls-files
# --modified --others --exclude-standard` output captured *immediately before
# the agent ran*, we subtract that set from the current set. The remainder is
# what newly appeared (or newly changed) during the agent's run — i.e., what
# the agent actually wrote. This makes the validator robust to any new tool a
# future contributor adds to the workflow without requiring a corresponding
# .gitignore entry.
#
# When $PRE_SNAPSHOT is unset (e.g. local invocation, or a workflow we haven't
# updated yet), we fall back to the legacy behavior so this script is
# backward-compatible.
#
# Known limitation: if a non-agent step creates an untracked, non-gitignored
# file and the agent then *modifies the content* of that same file (rather
# than creating something new), the validator will miss the modification —
# both pre and post lists contain the same path. The realistic exposure is
# tiny in this repo (lockfiles created by `npm install` fall under each
# agent's scope rules anyway; every other known tool artifact is gitignored).
# If this becomes a real concern, upgrade the snapshot to `sha256  path` and
# diff by content hash.
POST_LIST=$(git -C "$REPO_ROOT" ls-files --modified --others --exclude-standard | sort -u)

if [ -n "${PRE_SNAPSHOT:-}" ] && [ -f "$PRE_SNAPSHOT" ]; then
    CHANGED=$(comm -23 <(printf '%s\n' "$POST_LIST") <(sort -u "$PRE_SNAPSHOT"))
else
    echo "::warning::PRE_SNAPSHOT not set — falling back to legacy 'all-untracked-is-agent' attribution. Add a 'Snapshot worktree (pre-agent)' step to this job for accurate scope validation."
    CHANGED="$POST_LIST"
fi

# Drop paths that tooling may refresh but that are not meaningful "agent writes"
# (see pipeline/locks.yaml ignore_for_attribution).
if [ -n "$IGNORE" ]; then
  FILTERED=""
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    skip=false
    while IFS= read -r ign; do
      [ -z "$ign" ] && continue
      if [ "$file" = "$ign" ]; then
        skip=true
        break
      fi
    done <<< "$IGNORE"
    [ "$skip" = true ] && continue
    FILTERED+="${file}"$'\n'
  done <<< "$CHANGED"
  CHANGED=$(printf '%s' "$FILTERED" | sed '/^$/d')
fi

if [ -z "$CHANGED" ]; then
    echo "No files attributable to $AGENT_NAME — scope check passed"
    exit 0
fi

DENY_VIOLATIONS=""
SCOPE_VIOLATIONS=""
while IFS= read -r file; do
    [ -z "$file" ] && continue

    if [ -n "$DENY" ]; then
        DENIED=false
        while IFS= read -r pattern; do
            [ -z "$pattern" ] && continue
            if echo "$file" | grep -qE "$pattern"; then
                DENIED=true
                break
            fi
        done <<< "$DENY"
        if [ "$DENIED" = true ]; then
            DENY_VIOLATIONS="$DENY_VIOLATIONS\n  $file"
            continue
        fi
    fi

    MATCH=false
    while IFS= read -r pattern; do
        [ -z "$pattern" ] && continue
        if echo "$file" | grep -qE "$pattern"; then
            MATCH=true
            break
        fi
    done <<< "$ALLOWED"
    if [ "$MATCH" = false ]; then
        SCOPE_VIOLATIONS="$SCOPE_VIOLATIONS\n  $file"
    fi
done <<< "$CHANGED"

FAILED=0
if [ -n "$DENY_VIOLATIONS" ]; then
    echo "::error::$AGENT_NAME wrote to explicitly denied paths:$DENY_VIOLATIONS"
    FAILED=1
fi

if [ -n "$SCOPE_VIOLATIONS" ]; then
    echo "::error::$AGENT_NAME modified files outside its allowed write scope:$SCOPE_VIOLATIONS"
    FAILED=1
fi

if [ "$FAILED" -ne 0 ]; then
    exit 1
fi

echo "Scope check passed for $AGENT_NAME"
