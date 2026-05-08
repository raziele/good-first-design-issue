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
")

ALLOWED=$(echo "$PATTERNS" | awk '/^ALLOWED$/{flag=1;next}/^DENY$/{flag=0}flag')
DENY=$(echo "$PATTERNS"   | awk '/^DENY$/{flag=1;next}flag')

if [ -z "$ALLOWED" ]; then
    echo "No write permissions defined for $AGENT_NAME — skipping scope check"
    exit 0
fi

# Include both modified (tracked) and added (untracked, not gitignored) files.
# Plain `git diff --name-only` misses untracked files, which would let an
# agent slip a brand-new file into a denied path before the workflow's
# `git add` step.
CHANGED=$(git -C "$REPO_ROOT" ls-files --modified --others --exclude-standard | sort -u)

if [ -z "$CHANGED" ]; then
    echo "No files changed — scope check passed"
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
