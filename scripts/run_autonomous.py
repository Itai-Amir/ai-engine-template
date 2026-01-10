#!/usr/bin/env python3

import os
import json
import subprocess
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_PATH = os.path.join(REPO_ROOT, "state", "progress.json")
FEATURE_001_PATH = os.path.join(
    REPO_ROOT,
    "features",
    "001-persist-candidate-knowledge-pack.yml",
)

FEATURE_002_PATH = os.path.join(
    REPO_ROOT,
    "features",
    "002-load-knowledge-pack-immutable.yml",
)

# ---------------------------------------------------------------------------
# Canonical state
# ---------------------------------------------------------------------------

INITIAL_STATE: Dict[str, Any] = {
    "phase": "PLAN",
    "completed_features": [],
    "current_feature": None,
    "history": [],
}

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git(cmd: list[str]) -> None:
    subprocess.check_call(cmd, cwd=REPO_ROOT)

def ensure_git_identity() -> None:
    git(["git", "config", "user.name", "autonomous-engine"])
    git(["git", "config", "user.email", "autonomous@localhost"])

# ---------------------------------------------------------------------------
# State handling
# ---------------------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        return INITIAL_STATE.copy()

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)

# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------

def plan(state: Dict[str, Any]) -> None:
    state["phase"] = "PLAN"
    state["history"].append({"phase": "PLAN"})

def approve(state: Dict[str, Any]) -> None:
    state["phase"] = "APPROVE"
    state["history"].append({"phase": "APPROVE"})

def verify(state: Dict[str, Any]) -> None:
    state["phase"] = "VERIFY"
    state["history"].append({"phase": "VERIFY"})

# ---------------------------------------------------------------------------
# Feature discovery
# ---------------------------------------------------------------------------

def feature_002_defined() -> bool:
    return os.path.exists(FEATURE_002_PATH)
    
def feature_001_defined() -> bool:
    return os.path.exists(FEATURE_001_PATH)

# ---------------------------------------------------------------------------
# Feature 001 implementation
# ---------------------------------------------------------------------------

def implement_feature_001(state: Dict[str, Any]) -> None:
    if "001" in state["completed_features"]:
        return

    ensure_git_identity()

    src_dir = os.path.join(REPO_ROOT, "src")
    test_dir = os.path.join(REPO_ROOT, "tests")

    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    src_path = os.path.join(src_dir, "knowledge_pack.py")
    test_path = os.path.join(test_dir, "test_knowledge_pack_persistence.py")

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(
            """import json
from typing import Dict, Any


def persist_knowledge_pack(knowledge_pack: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge_pack, f, sort_keys=True, ensure_ascii=False)
"""
        )

    with open(test_path, "w", encoding="utf-8") as f:
        f.write(
            """import json
from src.knowledge_pack import persist_knowledge_pack


def test_persist_and_reload_roundtrip(tmp_path):
    knowledge_pack = {
        "name": "Alice",
        "skills": ["python", "ai"],
        "experience": 5,
    }

    output = tmp_path / "knowledge_pack.json"
    persist_knowledge_pack(knowledge_pack, str(output))

    with open(output, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded == knowledge_pack
"""
        )

    git(["git", "add", "src/knowledge_pack.py", "tests/test_knowledge_pack_persistence.py"])
    git(["git", "commit", "-m", "autonomous: implement feature 001 persist knowledge pack"])
    git(["git", "push", "origin", "HEAD:main"])

    state["completed_features"].append("001")
    state["history"].append({"implemented": "001"})

def implement_feature_002(state: Dict[str, Any]) -> None:
    if "002" in state["completed_features"]:
        return

    ensure_git_identity()

    src_path = os.path.join(REPO_ROOT, "src", "knowledge_pack.py")
    test_path = os.path.join(
        REPO_ROOT,
        "tests",
        "test_knowledge_pack_load_immutable.py",
    )

    # --- append implementation ---
    with open(src_path, "a", encoding="utf-8") as f:
        f.write(
            """

from types import MappingProxyType
from typing import Mapping, Any
import json


def load_knowledge_pack(path: str) -> Mapping[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return MappingProxyType(data)
"""
        )

    # --- test ---
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(
            """import json
import pytest
from src.knowledge_pack import load_knowledge_pack


def test_load_knowledge_pack_is_immutable(tmp_path):
    data = {"x": 1}
    path = tmp_path / "kp.json"
    with open(path, "w") as f:
        json.dump(data, f)

    kp = load_knowledge_pack(str(path))
    assert kp["x"] == 1

    with pytest.raises(TypeError):
        kp["x"] = 2
"""
        )

    git([
        "git",
        "add",
        "src/knowledge_pack.py",
        "tests/test_knowledge_pack_load_immutable.py",
    ])
    git([
        "git",
        "commit",
        "-m",
        "autonomous: implement feature 002 load knowledge pack immutable",
    ])
    git(["git", "push", "origin", "HEAD:main"])

    state["completed_features"].append("002")
    state["history"].append({"implemented": "002"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    os.chdir(REPO_ROOT)

    state = load_state()

    plan(state)
    approve(state)

    if feature_001_defined():
        implement_feature_001(state)

    if feature_002_defined():
        implement_feature_002(state)
            
    verify(state)
    save_state(state)

if __name__ == "__main__":
    main()
