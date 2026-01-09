#!/bin/bash
set -e

TEMPLATE_REPO="https://github.com/Itai-Amir/ai-engine-template.git"
RUNNER_DIR="runner/actions-runner"

echo "== AI Engine Template Setup =="

# ------------------------------------------------------------
# 1. Ensure git repository
# ------------------------------------------------------------
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not inside a git repository."
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "❌ Missing 'origin' remote."
  exit 1
fi

# ------------------------------------------------------------
# 2. Add template remote
# ------------------------------------------------------------
if git remote get-url template >/dev/null 2>&1; then
  echo "ℹ️ Template remote already exists."
else
  git remote add template "$TEMPLATE_REPO"
  echo "✅ Added template remote:"
  echo "   template → $TEMPLATE_REPO"
fi

git fetch template >/dev/null

# ------------------------------------------------------------
# 3. Check runner installation
# ------------------------------------------------------------
if [ ! -d "$RUNNER_DIR" ]; then
  echo "❌ GitHub Actions runner not installed."
  echo "Expected directory: $RUNNER_DIR"
  exit 1
fi

# ------------------------------------------------------------
# 4. Check runner status
# ------------------------------------------------------------
echo ""
echo "Checking runner status..."
./runner/status.sh

echo ""
echo "✅ Setup complete."
echo "You can now push code and CI will run automatically."
