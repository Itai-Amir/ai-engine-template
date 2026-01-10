#!/usr/bin/env python3

import os
import json
import subprocess
import importlib
from typing import Dict, Any, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(REPO_ROOT, "state", "progress.json")
PLAN_PATH = os.path.join(REPO_ROOT, "PROJECT_SPEC.md")
FEATURES_DIR = os.path.join(REPO_ROOT, "scripts", "features")
FEATURES_PKG = "scripts.features"

INITIAL_STATE = {
    "phase": "PLAN",
    "completed_features": [],
    "current_feature": None,
    "history": [],
}

# ---------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------

def git(cmd: List[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)

def ensure_git_identity() -> None:
    git(["git", "config", "user.name", "autonomous-engine"])
    git(["git", "config", "user.email", "autonomous@localhost"])

# ---------------------------------------------------------------------
# State
# ---------------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        return INITIAL_STATE.copy()
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

# ---------------------------------------------------------------------
# PLAN compilation
# ---------------------------------------------------------------------

def load_plan_features() -> List[str]:
    features: List[str] = []

    if not os.path.exists(PLAN_PATH):
        return features

    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# Feature "):
                fid = line.split("Feature ")[1].split(":")[0].strip()
                features.append(fid)

    return features

# ---------------------------------------------------------------------
# Feature scaffolding
# ---------------------------------------------------------------------

def scaffold_feature(feature_id: str) -> None:
    os.makedirs(FEATURES_DIR, exist_ok=True)
    path = os.path.join(FEATURES_DIR, f"feature_{feature_id}.py")

    if os.path.exists(path):
        return

    with open(path, "w", encoding="utf-8") as f:
        f.write(
            f'''FEATURE_ID = "{feature_id}"

def implement(state):
    raise NotImplementedError(
        "Feature {feature_id} is defined in PROJECT_SPEC.md "
        "but not implemented yet."
    )
'''
        )

    git(["git", "add", path])
    git([
        "git",
        "commit",
        "-m",
        f"scaffold: add feature {feature_id} implementation stub",
    ])
    git(["git", "push", "origin", "HEAD:main"])

    raise RuntimeError(
        f"Feature {feature_id} scaffolded. "
        "Implement it and rerun CI."
    )

# ---------------------------------------------------------------------
# Dynamic feature execution
# ---------------------------------------------------------------------

def implement_feature(feature_id: str, state: Dict[str, Any]) -> None:
    module_name = f"{FEATURES_PKG}.feature_{feature_id}"

    try:
        module = importlib.import_module(module_name)
    except ImportError:
        scaffold_feature(feature_id)

    if getattr(module, "FEATURE_ID", None) != feature_id:
        raise RuntimeError(f"FEATURE_ID mismatch in {module_name}")

    if not hasattr(module, "implement"):
        raise RuntimeError(f"No implement(state) in {module_name}")

    module.implement(state)

# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

def main() -> None:
    os.chdir(REPO_ROOT)
    ensure_git_identity()

    state = load_state()
    plan_features = load_plan_features()

    for fid in plan_features:
        if fid not in state["completed_features"]:
            state["current_feature"] = fid
            implement_feature(fid, state)
            state["completed_features"].append(fid)
            state["history"].append({"implemented": fid})

    state["current_feature"] = None
    state["phase"] = "VERIFY"
    save_state(state)

if __name__ == "__main__":
    main()
