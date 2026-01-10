#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from typing import List

from openai import OpenAI

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)

FEATURES_DIR = os.path.join(REPO_ROOT, "features")
STATE_DIR = os.path.join(REPO_ROOT, "state")
STATE_PATH = os.path.join(STATE_DIR, "progress.json")
PROMPTS_DIR = os.path.join(STATE_DIR, "prompts")
GLOBAL_CONVENTIONS_PATH = os.path.join(
    REPO_ROOT, "GLOBAL_EXECUTION_CONVENTIONS.md"
)

MODE = os.getenv("AUTONOMOUS_MODE", "execute")  # execute | prepare

client = None
if MODE == "execute":
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def load_global_conventions() -> str:
    with open(GLOBAL_CONVENTIONS_PATH, "r", encoding="utf-8") as f:
        return f.read()


def load_feature_plan(feature_id: str) -> str:
    path = os.path.join(FEATURES_DIR, f"{feature_id}.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_features() -> List[str]:
    features = []
    for name in os.listdir(FEATURES_DIR):
        if not name.endswith(".md"):
            continue
        base = name.replace(".md", "")
        if base[:3].isdigit():
            features.append(base)
    return sorted(features)


def load_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {"completed_features": []}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def build_prompt(feature_id: str) -> str:
    return f"""
You are an autonomous software compiler.

You MUST follow ALL instructions exactly.
You MUST NOT ask questions.
You MUST NOT invent behavior.

================ GLOBAL EXECUTION CONVENTIONS ================
{load_global_conventions()}

================ FEATURE PLAN ({feature_id}) =================
{load_feature_plan(feature_id)}

================ EXECUTION RULES =============================

- Implement the feature exactly as specified
- Modify only allowed files
- After implementation:
  - Run pytest
  - If tests pass, stop and return "DONE"
  - If tests fail, stop immediately

BEGIN.
""".strip()


def write_prompt(feature_id: str, prompt: str) -> None:
    os.makedirs(PROMPTS_DIR, exist_ok=True)
    path = os.path.join(PROMPTS_DIR, f"{feature_id}.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(prompt)


def run_llm(prompt: str) -> None:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a deterministic code generator."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    patch = response.choices[0].message.content
    process = subprocess.Popen(
        ["git", "apply"],
        stdin=subprocess.PIPE,
        cwd=REPO_ROOT,
        text=True,
    )
    process.communicate(patch)
    if process.returncode != 0:
        raise RuntimeError("Failed to apply patch from LLM output")


def git(cmd: List[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)


def main() -> None:
    features = list_features()
    state = load_state()
    completed = set(state.get("completed_features", []))

    print(f"AUTONOMOUS MODE: {MODE.upper()}")
    print(f"Found features: {', '.join(features)}")

    for feature_id in features:
        if feature_id in completed:
            continue

        prompt = build_prompt(feature_id)

        if MODE == "prepare":
            write_prompt(feature_id, prompt)
            print(f"✔ Prepared feature {feature_id}")
            continue

        run_llm(prompt)
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

    if MODE == "prepare":
        print("Preparation complete. No execution performed.")


if __name__ == "__main__":
    main()
