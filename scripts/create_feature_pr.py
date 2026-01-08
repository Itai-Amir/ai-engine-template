from pathlib import Path
import json


FEATURES_DIR = Path("../features")
STATE_PATH = Path("../state/progress.json")


def main():
    """
    Select the next uncompleted feature in lexical order.
    """
    features = sorted(p.stem for p in FEATURES_DIR.glob("F-*.yaml"))

    with open(STATE_PATH) as f:
        state = json.load(f)

    completed = set(state.get("completed_features", []))

    remaining = [f for f in features if f not in completed]

    if not remaining:
        print("No remaining features.")
        return

    next_feature = remaining[0]
    state["current_feature"] = next_feature
    state["phase"] = "APPROVE"

    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

    print(f"Selected next feature: {next_feature}")


if __name__ == "__main__":
    main()
