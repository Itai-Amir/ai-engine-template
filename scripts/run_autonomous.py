#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from typing import List

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

FEATURES_DIR = os.path.join(REPO_ROOT, "features")
STATE_DIR = os.path.join(REPO_ROOT, "state")
STATE_PATH = os.path.join(STATE_DIR, "progress.json")
GLOBAL_CONVENTIONS_PATH = os.path.join(
    REPO_ROOT, "GLOBAL_EXECUTION_CONVENTIONS.md"
)


def load_global_conventions() -> str:
    with open(GLOBAL_CONVENTIONS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_feature_plan(feature_id: str) -> str:
    path = os.path.join(FEATURES_DIR, f"{feature_id}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_features() -> List[str]:
    ids = []
    for name in os.listdir(FEATURES_DIR):
        if name.endswith(".md"):
            ids.append(name.replace(".md", ""))
    return sorted(ids)


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {
            "completed_features": []
        }
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def build_copilot_prompt(feature_id: str) -> str:
    global_rules = load_global_conventions()
    feature_plan = load_feature_plan(feature_id)

    return f"""
You are GitHub Copilot running in headless execution mode.

You MUST follow ALL instructions exactly.

================ GLOBAL EXECUTION CONVENTIONS ================
{global_rules}

================ FEATURE PLAN ({feature_id}) =================
{feature_plan}

================ EXECUTION RULES =============================

- Implement the feature exactly as specified
- Do not ask questions
- Do not invent behavior
- Do not modify files outside the allowed list
- After implementation:
  - Run pytest
  - If tests pass, commit exactly once
  - If tests fail, stop immediately

BEGIN.
""".strip()


def run_copilot(prompt: str) -> None:
    subprocess.run(
        ["copilot", "exec"],
        input=prompt,
        text=True,
        check=True,
    )


def git(cmd: List[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)


def main() -> None:
    features = list_features()
    state = load_state()
    completed = set(state.get("completed_features", []))

    for feature_id in features:
        if feature_id in completed:
            continue

        prompt = build_copilot_prompt(feature_id)
        run_copilot(prompt)

        subprocess.check_call(["pytest"], cwd=REPO_ROOT)

        git(["git", "add", "."])
        git([
            "git", "commit",
            "-m", f"feature {feature_id}: implemented autonomously"
        ])
        git(["git", "push", "origin", "main"])

        completed.add(feature_id)
        state["completed_features"] = sorted(completed)
        save_state(state)


if __name__ == "__main__":
    main()
