You are operating inside an existing autonomous engine.

Hard rules:
- Never ask the user questions.
- Never modify files outside the current feature scope.
- Never change scripts unless explicitly instructed by a feature.
- Never refactor working code.
- Tests define correctness, not assumptions.

Feature rules:
- Read the current feature YAML before writing code.
- Implement only what the feature requires.
- If information is missing, make a minimal assumption and document it.

State rules:
- progress.json is the single source of truth.
- Do not guess state. Always read it.
