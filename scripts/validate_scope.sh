#!/usr/bin/env bash
# Validate that an agent only modified files within its allowed write paths.
# Usage: scripts/validate_scope.sh <agent-name>
#
# Reads allowed write paths from pipeline/locks.yaml and checks git diff.

set -euo pipefail

AGENT_NAME="${1:?Usage: validate_scope.sh <agent-name>}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Extract write paths for this agent from locks.yaml.
# Converts glob patterns like "src/**" to regex prefixes like "^src/".
ALLOWED=$(python3 -c "
import yaml, sys
with open('$REPO_ROOT/pipeline/locks.yaml') as f:
    locks = yaml.safe_load(f)
perms = locks.get('permissions', {}).get('$AGENT_NAME', {})
for p in perms.get('write', []):
    # Turn 'src/**' into '^src/' for grep matching
    print('^' + p.replace('/**', '/'))
")

if [ -z "$ALLOWED" ]; then
    echo "No write permissions defined for $AGENT_NAME — skipping scope check"
    exit 0
fi

CHANGED=$(git -C "$REPO_ROOT" diff --name-only)

if [ -z "$CHANGED" ]; then
    echo "No files changed — scope check passed"
    exit 0
fi

VIOLATIONS=""
while IFS= read -r file; do
    MATCH=false
    while IFS= read -r pattern; do
        if echo "$file" | grep -qE "$pattern"; then
            MATCH=true
            break
        fi
    done <<< "$ALLOWED"
    if [ "$MATCH" = false ]; then
        VIOLATIONS="$VIOLATIONS\n  $file"
    fi
done <<< "$CHANGED"

if [ -n "$VIOLATIONS" ]; then
    echo "::error::$AGENT_NAME modified files outside its allowed scope:$VIOLATIONS"
    exit 1
fi

echo "Scope check passed for $AGENT_NAME"
