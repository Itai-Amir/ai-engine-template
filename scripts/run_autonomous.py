#!/usr/bin/env python3

import os
import json
import sys
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

def load_state() -> Dict[str, Any]:
    """
    Load engine state from disk.
    If this is the first run, bootstrap a canonical initial state.
    """
    if not os.path.exists(STATE_PATH):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        return INITIAL_STATE.copy()

    with open(STATE_PATH, "r") as f:
        state = json.load(f)

    if not is_valid_state(state):
        raise RuntimeError("Invalid progress.json structure")

    return state


def save_state(state: Dict[str, Any]) -> None:
    """
    Persist engine state to disk.
    """
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def is_valid_state(state: Dict[str, Any]) -> bool:
    """
    Validate state structure strictly.
    """
    if not isinstance(state, dict):
        return False

    required_keys = {
        "phase": str,
        "completed_features": list,
        "current_feature": (str, type(None)),
        "history": list,
    }

    for key, expected_type in required_keys.items():
        if key not in state:
            return False
        if not isinstance(state[key], expected_type):
            return False

    return True


# ---------------------------------------------------------------------------
# Autonomous lifecycle (skeleton – feature logic lives elsewhere)
# ---------------------------------------------------------------------------

def plan(state: Dict[str, Any]) -> None:
    state["phase"] = "PLAN"
    state["history"].append({"phase": "PLAN"})


def approve(state: Dict[str, Any]) -> None:
    state["phase"] = "APPROVE"
    state["history"].append({"phase": "APPROVE"})


def implement(state: Dict[str, Any]) -> None:
    state["phase"] = "IMPLEMENT"
    state["history"].append({"phase": "IMPLEMENT"})


def verify(state: Dict[str, Any]) -> None:
    state["phase"] = "VERIFY"
    state["history"].append({"phase": "VERIFY"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    state = load_state()

    # Simple deterministic lifecycle pass
    plan(state)
    approve(state)
    implement(state)
    verify(state)

    save_state(state)


if __name__ == "__main__":
    main()
