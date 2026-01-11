#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from openai import OpenAI

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURES_DIR = REPO_ROOT / "features"
STATE_DIR = REPO_ROOT / "state"
STATE_FILE = STATE_DIR / "progress.json"

AUTONOMOUS_MODE = os.environ.get("AUTONOMOUS_MODE", "execute").lower()
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

client = OpenAI()

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

def git(cmd: List[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)

def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

# ---------------------------------------------------------------------
# State
# ---------------------------------------------------------------------

def load_state() -> Dict:
    if not STATE_FILE.exists():
        return {"completed": []}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))

def save_state(state: Dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

# ---------------------------------------------------------------------
# Feature Discovery (numeric-only: 001.md, 050.md, etc.)
# ---------------------------------------------------------------------

def discover_features() -> List[Path]:
    return sorted(
        f for f in FEATURES_DIR.glob("*.md")
        if f.stem.isdigit()
    )

# ---------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------

def build_prompt(feature_id: str, feature_file: Path) -> str:
    spec = feature_file.read_text(encoding="utf-8")

    return f"""
You are an autonomous senior software engineer.

Your task:
Implement feature {feature_id} EXACTLY as specified.

Rules (MANDATORY):
- Output MUST be valid JSON
- Top-level key: "files"
- Each key is a file path relative to repo root
- Each value is FULL file content
- Do NOT output diffs
- Do NOT explain
- Do NOT include markdown
- Do NOT include text outside JSON
- Overwrite files if they already exist

Expected output format:
{{
  "files": {{
    "src/example.py": "full file content",
    "tests/test_example.py": "full file content"
  }}
}}

Feature specification:
{spec}
""".strip()

# ---------------------------------------------------------------------
# LLM Execution (file-based)
# ---------------------------------------------------------------------

def run_llm(prompt: str) -> Dict[str, Dict[str, str]]:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    content = response.choices[0].message.content
    return json.loads(content)

# ---------------------------------------------------------------------
# Main Engine
# ---------------------------------------------------------------------

def main() -> None:
    log(f"AUTONOMOUS MODE: {AUTONOMOUS_MODE}")

    state = load_state()
    completed = set(state.get("completed", []))

    feature_files = discover_features()
    log(f"Found {len(feature_files)} features")

    for idx, feature_file in enumerate(feature_files, start=1):
        fid = feature_file.stem
        prefix = f"[{idx}/{len(feature_files)}] Feature {fid}"

        if fid in completed:
            log(f"{prefix} — SKIP (already completed)")
            continue

        log(f"{prefix} — START")

        if AUTONOMOUS_MODE == "prepare":
            prompt = build_prompt(fid, feature_file)
            out = STATE_DIR / f"{fid}.prompt.txt"
            write_file(out, prompt)
            log(f"{prefix} — PREPARED")
            continue

        # EXECUTE
        prompt = build_prompt(fid, feature_file)
        result = run_llm(prompt)

        files = result.get("files")
        if not files:
            raise RuntimeError(f"{prefix}: LLM returned no files")

        for rel_path, content in files.items():
            write_file(REPO_ROOT / rel_path, content)

        git(["git", "add", "."])
        git(["git", "commit", "-m", f"feature {fid}: implemented autonomously"])
        git(["git", "push", "origin", "HEAD:main"])

        completed.add(fid)
        state["completed"] = sorted(completed)
        save_state(state)

        log(f"{prefix} — DONE")

    log("All features processed successfully")

# ---------------------------------------------------------------------

if __name__ == "__main__":
    main()
