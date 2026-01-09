#!/usr/bin/env bash
set -euo pipefail

echo "== AI Engine Runner Status =="

# -----------------------------
# Helpers
# -----------------------------
fail() {
  echo "❌ $1"
  exit 1
}

info() {
  echo "ℹ️ $1"
}

ok() {
  echo "✅ $1"
}

# -----------------------------
# Preconditions
# -----------------------------
command -v gh >/dev/null 2>&1 || fail "GitHub CLI (gh) not installed."
command -v git >/dev/null 2>&1 || fail "git not installed."

# -----------------------------
# GitHub CLI Auth Check
# -----------------------------
if ! gh auth status >/dev/null 2>&1; then
  fail "GitHub CLI not authenticated. Run: gh auth login"
fi

ok "GitHub CLI authenticated."

# -----------------------------
# Resolve Repository
# -----------------------------
REPO_URL=$(git remote get-url origin 2>/dev/null || true)
[[ -z "$REPO_URL" ]] && fail "Cannot determine git remote 'origin'."

# Normalize repo URL → OWNER/REPO
if [[ "$REPO_URL" == git@github.com:* ]]; then
  REPO_PATH="${REPO_URL#git@github.com:}"
  REPO_PATH="${REPO_PATH%.git}"
elif [[ "$REPO_URL" == https://github.com/* ]]; then
  REPO_PATH="${REPO_URL#https://github.com/}"
  REPO_PATH="${REPO_PATH%.git}"
else
  fail "Unsupported repository URL: $REPO_URL"
fi

ok "Repository: $REPO_PATH"

# -----------------------------
# Runner Process Check
# -----------------------------
RUNNER_DIR="runner/actions-runner"
[[ -d "$RUNNER_DIR" ]] || fail "Runner directory not found: $RUNNER_DIR"

if pgrep -f "Runner.Listener" >/dev/null 2>&1; then
  ok "Local runner process running."
else
  fail "Local runner process not running."
fi

# -----------------------------
# Runner ↔ Repo Validation
# -----------------------------
HOSTNAME=$(hostname)
info "Runner host: $HOSTNAME"

RUNNERS_JSON=$(gh api "repos/$REPO_PATH/actions/runners" 2>/dev/null) \
  || fail "Failed to query GitHub Actions runners via API."

RUNNER_FOUND=$(echo "$RUNNERS_JSON" | jq -r \
  ".runners[] | select(.name==\"$HOSTNAME\") | .name" || true)

[[ -z "$RUNNER_FOUND" ]] && fail "No runner registered in GitHub matching host: $HOSTNAME"

ok "Runner registered with repository."

# -----------------------------
# Workflow runs-on / label check
# -----------------------------
WORKFLOW_FILE=".github/workflows/healthcheck.yml"
[[ -f "$WORKFLOW_FILE" ]] || fail "Workflow file missing: $WORKFLOW_FILE"

RUNS_ON=$(grep -A2 "runs-on:" "$WORKFLOW_FILE" | tr -d '[],' | tail -n +2 | awk '{print $1}')

if [[ -n "$RUNS_ON" ]]; then
  info "Workflow runs-on label: $RUNS_ON"
fi

# -----------------------------
# CI Healthcheck (latest run)
# -----------------------------
RUNS_JSON=$(gh api "repos/$REPO_PATH/actions/runs?per_page=1" 2>/dev/null) \
  || fail "Failed to query workflow runs."

LATEST_STATUS=$(echo "$RUNS_JSON" | jq -r '.workflow_runs[0].conclusion // empty')

if [[ -z "$LATEST_STATUS" ]]; then
  info "No workflow runs yet."
else
  ok "Latest CI run status: $LATEST_STATUS"
fi

# -----------------------------
# Summary
# -----------------------------
echo
ok "Runner status OK."
