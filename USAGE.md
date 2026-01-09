# 🧑‍🏫 User Guide for a New Project Created from the Template
(Self-Hosted Runner + Autonomous CI)

This guide is written for users with no prior knowledge.  
Follow the steps **exactly in order** and everything will work.

---

## 🟢 Step 0 – Make Sure You Are in the Correct Project

Open a terminal on your computer and run:

```bash
cd ~/Projects/my-first-product
ls
```

You should see folders like:
```
scripts/
runner/
.github/
```

If you see the `runner/` folder, you are in the correct place.

---

## 🟢 Step 1 – Create an OPENAI_API_KEY (One-Time)

1. Open this page in your browser:
   https://platform.openai.com/api-keys
2. Log in or sign up
3. Click **Create new secret key**
4. Copy the key that starts with `sk-...`

⚠️ Save this key somewhere safe. You will use it in the next step.

---

## 🟢 Step 2 – Add OPENAI_API_KEY to GitHub

1. Open your repository on GitHub  
   Example:
   https://github.com/Itai-Amir/my-first-product

2. Click **Settings**
3. In the left menu, click:
   **Secrets and variables → Actions**
4. Click **New repository secret**
5. Fill in:
   - **Name**: `OPENAI_API_KEY`
   - **Secret**: paste the `sk-...` key
6. Click **Save secret**

✔ OpenAI setup is done. You will not touch this again.

---

## 🟢 Step 3 – Install the Self-Hosted Runner (One-Time per Machine)

In your terminal, inside the project:

```bash
cd runner
ls
```

You should see:
```
setup.sh
start.sh
README.md
```

### Run the setup script

```bash
./setup.sh https://github.com/Itai-Amir/my-first-product
```

The script will download the GitHub Actions runner and then pause, asking for a **runner token**.

---

## 🟢 Step 4 – Get the Runner Token from GitHub

1. In your browser, go to your repository
2. Navigate to:
   **Settings → Actions → Runners**
3. Click **New self-hosted runner**
4. GitHub will show instructions and a **temporary token**
5. Copy only the token

Return to the terminal and paste the token when prompted.

If successful, you will see:
```
Runner configured successfully
```

---

## 🟢 Step 5 – Start the Runner

Still inside the `runner` folder, run:

```bash
./start.sh
```

You should see:
```
Listening for Jobs
```

⚠️ **Do not close this terminal.**  
This process must keep running for CI to work.

---

## 🟢 Step 6 – Verify Everything Works

Open a new terminal window (or tab) and run:

```bash
git commit --allow-empty -m "Trigger CI"
git push
```

### What should happen

- On GitHub → **Actions**:
  - A workflow named **Autonomous Engine** starts running
- In the runner terminal:
  - You will see logs like:
    ```
    PLAN
    APPROVE
    IMPLEMENT
    VERIFY
    ```

🎉 That’s it. Autonomous CI is now running.

---

## 🧠 Quick Summary

- `OPENAI_API_KEY` → added once to GitHub Secrets
- `setup.sh` → run once to connect the machine
- `start.sh` → keep running
- Every `git push` → CI runs automatically

---

## 🧩 Important Notes

- The runner is tied to **this repository**
- The runner token is **single-use**
- Never commit API keys or tokens
- The runner process must be running for CI to execute

---

If something does not work, check:
- The runner is **Idle** in GitHub → Settings → Actions → Runners
- `start.sh` is still running
- `OPENAI_API_KEY` exists in GitHub Secrets
