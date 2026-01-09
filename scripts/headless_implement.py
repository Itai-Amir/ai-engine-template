import os
import subprocess
from pathlib import Path
import yaml
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

FEATURES_DIR = Path("../features")
SYSTEM_PROMPT = Path("../.copilot/system.prompt.md").read_text()
RULES_PROMPT = Path("../.copilot/rules.md").read_text()


def load_feature(feature_id):
    for f in FEATURES_DIR.glob(f"{feature_id}*.yaml"):
        return yaml.safe_load(f.read_text())
    raise RuntimeError(f"Feature YAML not found for {feature_id}")


def main():
    import json

    state = json.loads(Path("../state/progress.json").read_text())
    feature_id = state["current_feature"]

    feature = load_feature(feature_id)

    prompt = f"""
{SYSTEM_PROMPT}

{RULES_PROMPT}

Implement the following feature.

FEATURE ID: {feature["id"]}
TITLE: {feature.get("title")}
DESCRIPTION:
{feature.get("description")}

ACCEPTANCE CRITERIA:
{feature.get("acceptance_criteria")}

IMPORTANT:
- Modify only product code
- Do NOT modify engine or scripts
- Output code changes directly
"""

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    code = response.choices[0].message.content

    # Apply changes using git (safe, deterministic)
    patch_file = Path("/tmp/llm.patch")
    patch_file.write_text(code)

    subprocess.run(["git", "apply", str(patch_file)], check=True)


if __name__ == "__main__":
    main()
