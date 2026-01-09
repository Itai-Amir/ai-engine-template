import json
import sys
import os

from pathlib import Path

from create_feature_pr import main as create_features
from approve_feature import approve

STATE_PATH = Path("../state/progress.json")


def load_state():
    if not os.path.exists(STATE_PATH):
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        return {
            "phase": "PLAN",
            "history": []
        }

    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    # Explicit planning mode (Approach B)
    if "--auto-plan" in sys.argv:
        import subprocess
        subprocess.run(["python", "copilot_plan.py"], check=True)
        return

    while True:
        state = load_state()

        # Fail fast on corrupted state
        if "phase" not in state or "current_feature" not in state:
            raise RuntimeError("Invalid progress.json structure")

        phase = state["phase"]
        feature = state["current_feature"]

        if phase == "BOOTSTRAP":
            create_features()
            state["phase"] = "PLANNING"

        elif phase == "PLANNING":
            if state["current_feature"] is None:
                create_features()
                state = load_state()

                if state["current_feature"] is None:
                    save_state(state)
                    print("No remaining features. Engine idle.")
                    break

        elif phase == "APPROVE":
            approve(feature)

            # APPROVE commits to disk → move to IMPLEMENT and stop
            state = load_state()
            state["phase"] = "IMPLEMENT"
            save_state(state)
            return

        elif phase == "IMPLEMENT":
            import subprocess
            subprocess.run(["python", "headless_implement.py"], check=True)

            # IMPLEMENT is blocking → advance to VERIFY and stop
            state["phase"] = "VERIFY"
            save_state(state)
            return

        elif phase == "VERIFY":
            import subprocess

            feature_file = Path(f"../features/{feature}.yaml")
            if not feature_file.exists():
                raise RuntimeError(f"Missing feature file: {feature_file}")

            verify_command = None
            with open(feature_file) as f:
                for line in f:
                    if line.strip().startswith("verify_command:"):
                        verify_command = line.split(":", 1)[1].strip()
                        break

            if verify_command:
                try:
                    subprocess.run(
                        verify_command.split(),
                        check=True,
                        cwd=Path("..")
                    )
                except subprocess.CalledProcessError:
                    print("VERIFY FAILED")
                    return
            else:
                print("No verify_command; marking feature as completed.")

            state["phase"] = "COMPLETED"
            if feature not in state["completed_features"]:
                state["completed_features"].append(feature)

        elif phase == "COMPLETED":
            state["current_feature"] = None
            state["phase"] = "PLANNING"

        save_state(state)


if __name__ == "__main__":
    main()
