from pathlib import Path


def main():
    plan_path = Path("../PROJECT_SPEC.md")
    features_dir = Path("../features")

    if not plan_path.exists():
        print("PROJECT_SPEC.md not found. Aborting planning.")
        return

    features_dir.mkdir(exist_ok=True)

    prompt = """
Read PROJECT_SPEC.md and generate a set of feature YAML files in features/.

Rules:
- Output ONLY YAML files.
- One feature per file.
- Feature IDs must be incremental (F-1000, F-1100, ...).
- Do NOT implement code.
- Do NOT modify engine or scripts.
- Each feature must include acceptance_criteria.
"""

    print("=== Copilot PLAN PROMPT ===")
    print(prompt.strip())
    print("=== END PROMPT ===")
    print("Open Copilot Chat and paste the prompt above.")


if __name__ == "__main__":
    main()
