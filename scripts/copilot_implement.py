import json
from pathlib import Path
import subprocess


STATE_PATH = Path("../state/progress.json")


def load_state():
    with open(STATE_PATH) as f:
        return json.load(f)


def main():
    state = load_state()
    feature = state.get("current_feature")

    if not feature:
        print("No current feature to implement.")
        return

    prompt = f"""
Implement the feature according to features/{feature}.yaml.
Follow .copilot/system.prompt.md and .copilot/rules.md.
Do not modify engine or script files.
"""

    print("=== Copilot IMPLEMENT PROMPT ===")
    print(prompt.strip())
    print("=== END PROMPT ===")

    print(
        "Open Copilot Chat and paste the prompt above to implement the feature."
    )


if __name__ == "__main__":
    main()
