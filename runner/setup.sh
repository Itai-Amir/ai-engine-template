#!/bin/bash
set -e

echo "== GitHub Self-Hosted Runner Setup =="

if [ -z "$1" ]; then
  echo "Usage: ./setup.sh <GITHUB_REPO_URL>"
  exit 1
fi

REPO_URL="$1"

mkdir -p actions-runner
cd actions-runner

curl -L -o runner.tar.gz https://github.com/actions/runner/releases/download/v2.330.0/actions-runner-osx-x64-2.330.0.tar.gz
tar xzf runner.tar.gz
rm runner.tar.gz

echo ""
echo "Go to:"
echo "  $REPO_URL/settings/actions/runners"
echo "Click 'New self-hosted runner' and copy the token."
echo ""
read -p "Paste runner token here: " TOKEN

./config.sh --url "$REPO_URL" --token "$TOKEN"

echo "Runner configured."
