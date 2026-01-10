#!/usr/bin/env python3

import os
import sys
import json
import subprocess
from typing import List
from datetime import datetime
from openai import OpenAI

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEATURES_DIR = os.path.join(REPO_ROOT, "features")
STATE_DIR = os.path.join(REPO_ROOT, "state")
PROMPTS_DIR = os.path.join(STATE_DIR, "prompts")
STATE_FILE = os.path.join(STATE_DIR, "progress.json")
GLOBAL_CONVENTIONS = os.path.join(FEATURES_DIR, "GLOBAL_EXECUTION_CONVENTIONS.md")

AUTONOMOUS_MODE = os.getenv("AUTONOMOUS_MODE", "execute")
MODEL_NAME = "gpt-4.1-mini"

sys.path.insert(0, REPO_ROOT)

# ------------------------------------------------------------

def now():
    return datetime.utcnow().strftime("%H:%M:%S")

def log(msg):
    print(f"[{now()}] {msg}", flush=True)

def git(cmd):
    subprocess.check_call(cmd, cwd=REPO_ROOT)

# ------------------------------------------------------------

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"completed_features": []}
    with open(STATE_FILE) as f:
        return json.load(f)

def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ------------------------------------------------------------

def list_features():
    return sorted(
        f[:-3]
        for f in os.listdir(FEATURES_DIR)
        if f.endswith(".md") and f[:3].isdigit()
    )

def read(path):
    with open(path) as f:
        return f.read()

# ------------------------------------------------------------

def build_prompt(feature_id, retry=False):
    retry_note = ""
    if retry:
        retry_note = """
PREVIOUS ATTEMPT FAILED.
Fix the diff. Ensure hunks, file headers, and line numbers are correct.
Return a FULL unified diff.
"""

    return f"""
You are an autonomous software engineer acting as a deterministic compiler.

GLOBAL EXECUTION CONVENTIONS:
{read(GLOBAL_CONVENTIONS)}

FEATURE PLAN:
{read(os.path.join(FEATURES_DIR, f"{feature_id}.md"))}

{retry_note}

OUTPUT FORMAT (MANDATORY):
- Output ONLY a valid unified git diff.
- Must start with: diff --git
- No explanations.
- No markdown.
- No extra text.
- If no changes are required, output EMPTY.
""".strip()

# ------------------------------------------------------------

def run_llm(prompt):
    client = OpenAI()
    r = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You generate valid unified git diffs only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return (r.choices[0].message.content or "").strip()

# ------------------------------------------------------------

def apply_patch(patch):
    if not patch.startswith("diff --git"):
        return False

    p = subprocess.Popen(
        ["git", "apply"],
        stdin=subprocess.PIPE,
        cwd=REPO_ROOT,
        text=True,
    )
    p.communicate(patch)
    return p.returncode == 0

# ------------------------------------------------------------

def main():
    log(f"AUTONOMOUS MODE: {AUTONOMOUS_MODE}")

    os.makedirs(PROMPTS_DIR, exist_ok=True)
    state = load_state()
    done = set(state["completed_features"])

    features = list_features()
    total = len(features)
    log(f"Found {total} features")

    for i, fid in enumerate(features, 1):
        if fid in done:
            continue

        prefix = f"[{i}/{total}] Feature {fid}"
        log(f"{prefix} — START")

        if AUTONOMOUS_MODE == "prepare":
            with open(os.path.join(PROMPTS_DIR, f"{fid}.txt"), "w") as f:
                f.write(build_prompt(fid))
            log(f"{prefix} — PREPARED")
            continue

        # attempt 1
        patch = run_llm(build_prompt(fid))
        if patch and apply_patch(patch):
            success = True
        else:
            # rollback partial changes before retry
            log(f"{prefix} — CLEAN WORKTREE BEFORE RETRY")
            git(["git", "reset", "--hard", "HEAD"])

            with open(os.path.join(STATE_DIR, f"{fid}.failed.diff"), "w") as f:
                f.write(patch or "")

            log(f"{prefix} — RETRY")
            patch = run_llm(build_prompt(fid, retry=True))
            success = patch and apply_patch(patch)
        

        if not success:
            raise RuntimeError(f"{prefix}: failed to apply valid diff after retry")

        status = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
        ).strip()

        if status:
            git(["git", "add", "."])
            git(["git", "commit", "-m", f"feature {fid}: implemented autonomously"])
            git(["git", "push", "origin", "main"])
            log(f"{prefix} — COMMITTED")
        else:
            log(f"{prefix} — NO CHANGES")

        done.add(fid)
        save_state({"completed_features": sorted(done)})
        log(f"{prefix} — DONE")

    log("All features processed successfully")

if __name__ == "__main__":
    main()
