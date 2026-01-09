#!/bin/bash
set -e

# ------------------------------------------------------------
# Dependencies
# ------------------------------------------------------------
for cmd in git gh jq pgrep; do
  if ! command -v $cmd >/dev/null 2>&1; then
    echo "❌ Missing dependency: $cmd"
    exit 1
  fi
done

if ! gh auth status >/dev/null 2>&1; then
  echo "❌ GitHub CLI not authenticated."
  echo "Run: gh auth login"
  exit 1
fi

# ------------------------------------------------------------
# Repo resolution
# ------------------------------------------------------------
REPO_URL=$(git remote get-url origin)
REPO_SLUG=$(echo "$REPO_URL" | sed -E 's#.*/([^/]+/[^/.]+)(\.git)?#\1#')
HOSTNAME=$(hostname)

echo "Repository: $REPO_SLUG"
echo "Runner host: $HOSTNAME"
echo ""

# ------------------------------------------------------------
# Local runner process
# ------------------------------------------------------------
if pgrep -f Runner.Listener >/dev/null; then
  echo "✅ Local runner process running."
else
  echo "❌ Runner process not running."
  exit 1
fi

# ------------------------------------------------------------
# GitHub runner status
# ------------------------------------------------------------
RUNNERS_JSON=$(gh api "repos/$REPO_SLUG/actions/runners")

RUNNER=$(echo "$RUNNERS_JSON" | jq -r \
  ".runners[] | select(.name==\"$HOSTNAME\")")

if [ -z "$RUNNER" ]; then
  echo "❌ This machine is NOT registered as a runner for this repo."
  exit 1
fi

STATUS=$(echo "$RUNNER" | jq -r .status)
BUSY=$(echo "$RUNNER" | jq -r .busy)
OS=$(echo "$RUNNER" | jq -r .os)
VERSION=$(echo "$RUNNER" | jq -r .version)

echo "Runner status: $STATUS"
echo "Runner busy:   $BUSY"
echo "Runner OS:     $OS"
echo "Runner version:$VERSION"
echo ""

if [ "$STATUS" != "online" ]; then
  echo "❌ Runner is not online."
  exit 1
fi

# ------------------------------------------------------------
# Label matching (runs-on)
# ------------------------------------------------------------
WORKFLOW_LABELS=$(grep -R "runs-on" .github/workflows \
  | sed -E 's/.*runs-on: *//g' \
  | tr -d '[],' \
  | tr ' ' '\n' \
  | sort -u)

RUNNER_LABELS=$(echo "$RUNNER" | jq -r '.labels[].name')

echo "Workflow labels:"
echo "$WORKFLOW_LABELS"
echo ""
echo "Runner labels:"
echo "$RUNNER_LABELS"
echo ""

for label in $WORKFLOW_LABELS; do
  if ! echo "$RUNNER_LABELS" | grep -qx "$label"; then
    echo "❌ Missing runner label: $label"
    exit 1
  fi
done

echo "✅ Runner labels match workflows."

# ------------------------------------------------------------
# OS / Arch check
# ------------------------------------------------------------
ARCH=$(uname -m)
echo "Runner architecture: $ARCH"

# ------------------------------------------------------------
# Version drift
# ------------------------------------------------------------
LATEST=$(curl -s https://api.github.com/repos/actions/runner/releases/latest \
  | jq -r .tag_name | sed 's/v//')

echo "Latest runner version: $LATEST"

if [ "$VERSION" != "$LATEST" ]; then
  echo "⚠️ Runner version is outdated."
else
  echo "✅ Runner version is up to date."
fi

# ------------------------------------------------------------
# CI healthcheck
# ------------------------------------------------------------
LAST_RUN=$(gh run list --limit 1 --json conclusion \
  | jq -r '.[0].conclusion')

echo "Last CI run: $LAST_RUN"

if [ "$LAST_RUN" != "success" ]; then
  echo "⚠️ CI healthcheck not clean."
else
  echo "✅ CI healthcheck OK."
fi

echo ""
echo "Runner status: OK"
