#!/usr/bin/env bash
set -e

echo "== AI Engine Runner Status =="

gh auth status >/dev/null && echo "✅ GitHub CLI authenticated"
echo "Repository: $(git remote get-url origin)"
echo "Runner host: $(hostname)"
