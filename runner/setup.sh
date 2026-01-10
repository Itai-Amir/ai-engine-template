#!/usr/bin/env bash
set -e

echo "== AI Engine Template Setup =="

if ! git remote | grep -q template; then
  git remote add template https://github.com/Itai-Amir/ai-engine-template.git
  echo "Added template remote"
fi

git fetch template
echo "Template ready"
