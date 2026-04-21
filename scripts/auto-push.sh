#!/bin/bash
# auto-push.sh — Auto commit and push all changes to GitHub
# Usage: bash scripts/auto-push.sh "your commit message"
# Or just: bash scripts/auto-push.sh  (uses timestamp as message)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# Default commit message
MSG="${1:-"chore: auto-sync $(date '+%Y-%m-%d %H:%M')"}"

echo "📦 Staging all changes..."
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "✅ Nothing to commit — working tree clean."
  exit 0
fi

echo "💾 Committing: $MSG"
git commit -m "$MSG"

echo "🚀 Pushing to origin/main..."
git push origin main

echo "✅ Done! Check: https://github.com/YongWilliam-ai/polyalpha-protocol"
