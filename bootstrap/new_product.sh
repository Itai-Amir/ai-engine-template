#!/bin/bash
set -e

TEMPLATE_REPO="https://github.com/Itai-Amir/ai-engine-template.git"

echo "== AI Engine Template Bootstrap =="

# 1. Ensure git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ This directory is not a git repository"
  exit 1
fi

# 2. Check origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "❌ No 'origin' remote found. Did you clone the product repo?"
  exit 1
fi

# 3. Add template remote if missing
if git remote get-url template >/dev/null 2>&1; then
  echo "ℹ️ Template remote already exists"
else
  git remote add template "$TEMPLATE_REPO"
  echo "✅ Added template remote:"
  echo "   template → $TEMPLATE_REPO"
fi

# 4. Fetch template
git fetch template

echo ""
echo "Bootstrap complete."
echo ""
echo "Next steps:"
echo "  - Develop ONLY product code in this repo"
echo "  - To upgrade from template:"
echo "      git fetch template"
echo "      git merge template/main"
