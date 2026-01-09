# AI Engine Template – Usage Guide

This repository is a **production-grade template** for building AI-powered products with a fully autonomous feature lifecycle and CI integration.

The template is **feature-complete (v1.0)** and designed to be:
- Minimal
- Deterministic
- Copilot-friendly
- Runner-based (no GitHub-hosted runners required)
- Safe to upgrade via upstream merges

---

## 1. Repository Model

Every product repository created from this template:

- Is generated using **GitHub “Use this template”**
- Automatically adds the template as an upstream remote named `template`
- Receives improvements via:
  ```bash
  git fetch template
  git merge template/main
  ```

The template itself is treated as **read-only infrastructure**.

---

## 2. One-Time Setup (New Product)

### 2.1 GitHub Secret

Add the following GitHub Actions secret:

- `OPENAI_API_KEY`

This is required for autonomous execution.

---

### 2.2 Runner Setup

On the machine that will act as the **self-hosted runner**:

```bash
./runner/setup.sh
```

This script:
- Registers the GitHub runner
- Validates OS / architecture
- Adds the `template` upstream remote
- Ensures repo ↔ runner compatibility

⚠️ The runner is installed as a **background service**.  
You do **not** start it manually.

---

### 2.3 Verification

Check runner and CI health at any time:

```bash
./runner/status.sh
```

This validates:
- Runner process is alive
- Repo ↔ runner match
- `runs-on` / labels alignment
- OS / architecture compatibility
- Runner version drift
- GitHub Actions health via API

---

## 3. Daily Development Workflow

### 3.1 Normal Development

Work as with any standard repository:

```bash
git checkout -b feature/my-change
# make changes
git commit -m "..."
git push
```

On every push:
- CI runs automatically
- The self-hosted runner is used
- Health checks are enforced

---

### 3.2 Autonomous Feature Execution

The template supports a **fully autonomous lifecycle**:

```
PLAN → APPROVE → IMPLEMENT → VERIFY
```

To run it locally or in CI:

```bash
python scripts/run_autonomous.py
```

Characteristics:
- No interactive questions
- Deterministic execution
- Safe to run repeatedly
- Designed for Copilot Agent / Chat usage

---

## 4. Copilot Usage Model

This template is optimized for **Copilot-driven implementation**.

Key principles:
- Copilot executes, not designs the system
- No IDE lock-in
- No GitHub hacks
- No runtime prompting

The autonomous script is the **single entry point**.

---

## 5. CI Model

### 5.1 GitHub Actions

The repository includes:

```
.github/workflows/healthcheck.yml
```

This workflow:
- Ensures the runner is healthy
- Prevents silent CI degradation
- Fails fast on environment drift

---

### 5.2 Self-Hosted Runner Only

- GitHub-hosted runners are intentionally **not used**
- All CI runs on your controlled infrastructure
- Deterministic OS and architecture

---

## 6. Upgrading from the Template

The template is frozen at **v1.0**, but may receive safe upgrades.

To upgrade a product repo:

```bash
git fetch template
git merge template/main
```

Guidelines:
- Expect **non-breaking** changes only
- Resolve conflicts once
- Never modify template-owned files unless required

---

## 7. What This Template Intentionally Does NOT Do

By design, this template avoids:
- Web dashboards
- Custom GitHub Apps
- YAML-based orchestration frameworks
- Plugin systems
- AI-driven CI logic
- Over-engineered abstractions

Simplicity and predictability are explicit goals.

---

## 8. Expected User Experience (Summary)

For a new product:

1. Add `OPENAI_API_KEY` to GitHub Secrets
2. Run `./runner/setup.sh`
3. Push code
4. CI works automatically

No further manual steps are required.

---

## 9. Support Model

This template assumes:
- Strong engineering discipline
- Familiarity with Git and CI
- Intentional changes only

If something fails, the system is designed to tell you **exactly why**.

---

## 10. License / Ownership

This template is infrastructure.
Your product code remains fully yours.
