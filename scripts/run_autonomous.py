import json
from pathlib import Path

from create_feature_pr import main as create_features
from approve_feature import approve
from implement_feature import implement
from verify_feature import verify
from recover import recover


STATE_PATH = Path("../state/progress.json")


def load_state():
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def main():
    state = load_state()

    phase = state["phase"]
    feature = state["current_feature"]

    if phase == "BOOTSTRAP":
        create_features()
        state["phase"] = "PLANNING"

    elif phase == "PLANNING":
        create_features()
        state = load_state()

    elif phase == "APPROVE":
        approve(feature)
        state["phase"] = "IMPLEMENT"

    elif phase == "IMPLEMENT":
        import subprocess
        subprocess.run(["python", "copilot_implement.py"], check=True)
        state["phase"] = "VERIFY"

    elif phase == "VERIFY":
        import subprocess
        from pathlib import Path

        feature_file = Path(f"../features/{feature}.yaml")
        verify_command = None

        with open(feature_file) as f:
            for line in f:
                if line.strip().startswith("verify_command:"):
                    verify_command = line.split(":", 1)[1].strip()
                    break

        if verify_command:
            subprocess.run(
                verify_command.split(),
                check=True,
                cwd=Path("..")
            )

        state["phase"] = "COMPLETED"
        state["completed_features"].append(feature)

    elif phase == "COMPLETED":
        state["current_feature"] = None
        state["phase"] = "PLANNING"
    
    save_state(state)
    print(f"Phase completed: {phase}")


if __name__ == "__main__":
    main()
