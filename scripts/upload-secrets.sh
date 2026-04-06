#!/usr/bin/env bash
# Upload required secrets to GitHub Actions.
# Usage: scripts/upload-secrets.sh
#
# Expects secret files under .secrets/ (git-ignored).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SECRETS_DIR="$REPO_ROOT/.secrets"

# --- Validate prerequisites ------------------------------------------------

if [ ! -f "$SECRETS_DIR/cursor-api-key" ]; then
    echo "Missing: .secrets/cursor-api-key"
    echo "Create the file with your Cursor API key, then re-run this script."
    exit 1
fi

# --- Confirm ----------------------------------------------------------------

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "<unknown>")
echo "This will upload secrets to GitHub repo: $REPO"
echo ""
echo "  CURSOR_API_KEY  <- .secrets/cursor-api-key"
echo ""
read -rp "Continue? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[yY]$ ]]; then
    echo "Aborted."
    exit 0
fi

# --- Upload -----------------------------------------------------------------

gh secret set CURSOR_API_KEY < "$SECRETS_DIR/cursor-api-key"
echo "Uploaded CURSOR_API_KEY"

echo "Done."
