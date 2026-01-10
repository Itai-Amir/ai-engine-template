#!/usr/bin/env python3

import os
import sys
import json
import subprocess
from typing import List
from openai import OpenAI

# -------------------------
# Paths & constants
# -------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEATURES_DIR = os.path.join(REPO_ROOT, "features")
STATE_DIR = os.path.join(REPO_ROOT, "state")
PROMPTS_DIR = os.path.join(STATE_DIR, "prompts")
STATE_FILE = os.path.join(STATE_DIR, "progress.json")
GLOBAL_CONVENTIONS = os.path.join(FEATURES_DIR, "GLOBAL_EXECUTION_CONVENTIONS.md")

AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "execute")  # prepare | execute
MODEL_NAME = "gpt-4.1-mini"

sys.path.insert(0, REPO_ROOT)

# -------------------------
# Utilities
# -------------------------

def git(cmd: List[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)

def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {
            "completed_features": [],
        }
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def list_features() -> List[str]:
    features = []
    for name in os.listdir(FEATURES_DIR):
        if not name.endswith(".md"):
            continue
        base = name.replace(".md", "")
        if base[:3].isdigit():
            features.append(base)
    return sorted(features)

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# -------------------------
# Prompt construction
# -------------------------

def build_prompt(feature_id: str) -> str:
    global_rules = read_file(GLOBAL_CONVENTIONS)
    feature_plan = read_file(os.path.join(FEATURES_DIR, f"{feature_id}.md"))

    return f"""
You are an autonomous software engineer.

GLOBAL EXECUTION RULES:
{global_rules}

FEATURE PLAN:
{feature_plan}

EXECUTION RULES:
- Implement the feature exactly as specified.
- Modify or create files as needed.
- Add or update tests if required.
- Ensure all tests pass.

OUTPUT FORMAT (MANDATORY):
- Output ONLY a valid unified git diff.
- The diff MUST start with: diff --git
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT include code blocks.
- Do NOT include the word DONE.
- If no changes are required, output an EMPTY string.
""".strip()

# -------------------------
# LLM execution
# -------------------------

def run_llm(prompt: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a deterministic code generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return response.choices[0].message.content or ""

# -------------------------
# Main flow
# -------------------------

def main() -> None:
    print(f"AUTONOMOUS MODE: {AUTONOMOUS_MODE}")

    os.makedirs(PROMPTS_DIR, exist_ok=True)
    state = load_state()
    completed = set(state.get("completed_features", []))

    features = list_features()
    print(f"Found features: {', '.join(features)}")

    for feature_id in features:
        if feature_id in completed:
            continue

        prompt = build_prompt(feature_id)

        if AUTONOMOUS_MODE == "prepare":
            with open(os.path.join(PROMPTS_DIR, f"{feature_id}.txt"), "w", encoding="utf-8") as f:
                f.write(prompt)
            print(f"✔ Prepared feature {feature_id}")
            continue

        # EXECUTE MODE
        patch = run_llm(prompt).strip()

        if not patch:
            print(f"ℹ️ Feature {feature_id}: LLM returned empty diff (no changes).")
            completed.add(feature_id)
            save_state({"completed_features": sorted(completed)})
            continue

        process = subprocess.Popen(
            ["git", "apply"],
            stdin=subprocess.PIPE,
            cwd=REPO_ROOT,
            text=True,
        )
        process.communicate(patch)

        if process.returncode != 0:
            raise RuntimeError(
                f"Feature {feature_id}: LLM output was not a valid git diff. Aborting."
            )

        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()

        if status:
            git(["git", "add", "."])
            git([
                "git", "commit",
                "-m", f"feature {feature_id}: implemented autonomously"
            ])
            git(["git", "push", "origin", "main"])
            print(f"✔ Feature {feature_id} committed")
        else:
            print(f"ℹ️ Feature {feature_id}: nothing to commit")

        completed.add(feature_id)
        save_state({"completed_features": sorted(completed)})

    print("All features processed successfully.")

# -------------------------
# Entrypoint
# -------------------------

if __name__ == "__main__":
    main()
