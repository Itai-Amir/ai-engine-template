#!/usr/bin/env python3

import os
import json
from typing import Dict, Any

STATE_PATH = "../state/progress.json"

# ---------------------------------------------------------------------------
# Canonical engine state
# ---------------------------------------------------------------------------

INITIAL_STATE: Dict[str, Any] = {
    "phase": "PLAN",
    "completed_features": [],
    "current_feature": None,
    "history": []
}


# ---------------------------------------------------------------------------
# State handling
# ---------------------------------------------------------------------------

def is_valid_state(state: Dict[str, Any]) -> bool:
    if not isinstance(state, dict):
        return False

    required = {
        "phase": str,
        "completed_features": list,
        "current_feature": (str, type(None)),
        "history": list,
    }

    for key, expected_type in required.items():
        if key not in state:
            return False
        if not isinstance(state[key], expected_type):
            return False

    return True


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        return INITIAL_STATE.copy()

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        state = json.load(f)

    if not is_valid_state(state):
        raise RuntimeError("Invalid progress.json structure")

    return state


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Lifecycle phases
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
# Feature 001 — Persist Candidate Knowledge Pack
# ---------------------------------------------------------------------------

def implement_feature_001_persist_knowledge_pack(state: Dict[str, Any]) -> None:
    if "001" in state["completed_features"]:
        return

    os.makedirs("src", exist_ok=True)
    os.makedirs("tests", exist_ok=True)
    os.makedirs("state", exist_ok=True)

    src_path = "src/knowledge_pack.py"
    test_path = "tests/test_knowledge_pack_persistence.py"

    # --- implementation ---
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(
            """import json
from typing import Dict, Any


def persist_knowledge_pack(knowledge_pack: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(knowledge_pack, f, sort_keys=True, ensure_ascii=False)
"""
        )

    # --- test ---
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(
            """import json
from src.knowledge_pack import persist_knowledge_pack


def test_persist_and_reload_roundtrip(tmp_path):
    knowledge_pack = {
        "name": "Alice",
        "skills": ["python", "ai"],
        "experience": 5
    }

    output = tmp_path / "knowledge_pack.json"
    persist_knowledge_pack(knowledge_pack, str(output))

    with open(output, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded == knowledge_pack
"""
        )

    os.system("git add src/knowledge_pack.py tests/test_knowledge_pack_persistence.py")
    os.system('git commit -m "autonomous: implement feature 001 persist knowledge pack"')

    state["completed_features"].append("001")
    state["history"].append({"implemented": "001"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    state = load_state()

    plan(state)
    approve(state)

    implement_feature_001_persist_knowledge_pack(state)

    verify(state)
    save_state(state)


if __name__ == "__main__":
    main()
