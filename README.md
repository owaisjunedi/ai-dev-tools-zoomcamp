# Repository for AI Dev Tools Zoomcamp


## 📋 1. Django Todo App

This repository contains a feature-rich **Django Todo Application** with a Retro 90s aesthetic completed as "Vibe-Coding". The app includes task management, calendar views, priority levels, tagging system, and more.

👉 **For detailed information**, see the [Todo App README](todo-app-django/README.md) and [Educational Guide](todo-app-django/INFORMATION.md).

## Initial Setup & Prerequisites

1. **Download Tools:**
   - Download and install [GitHub CLI](https://cli.github.com/).
   - Download and install Antigravity IDE.

2. **Open Terminal:**
   - Open **Git CMD** (or PowerShell/Terminal) as **Administrator**.

3. **Authenticate:**
   Run the following commands to authenticate:
   ```bash
   gh auth login
   ```
   Then, authenticate specifically with codespace permissions:
   ```bash
   gh auth login -s codespace
   ```

4. **Connect:**
   ```bash
   gh cs ssh
   ```

## Detailed Configuration Steps

Follow these detailed steps to configure your environment, create a GitHub Codespace, and connect to it via SSH for use with the Antigravity IDE.

### 1. Authenticate with GitHub CLI
Ensure you have the necessary permissions (scopes) to manage codespaces.
```bash
gh auth login -s codespace
```
Follow the interactive prompts to complete the login process via your browser.

### 2. Create or Select a Codespace
List your existing codespaces or create a new one.
```bash
gh cs
```
- If you don't have a codespace for this repo, choose the option to create a new one.
- If you already have one, note its name.

### 3. Configure SSH Access
Generate the SSH configuration required to connect to your codespace.
```bash
gh cs ssh --config
```
**Action:** Copy the output from this command and append it to your local SSH configuration file (usually located at `~/.ssh/config` on macOS/Linux or `C:\Users\YourUser\.ssh\config` on Windows).

#### Example SSH Configuration
Here is an example of what the SSH configuration content might look like (Windows example):

```text
Host cs.<codespace_code>.main
        User codespace
        ProxyCommand C:\Program Files\GitHub CLI\gh.exe cs ssh -c <codespace_code> --stdio -- -i C:\Users\YourUser\.ssh/codespaces.auto
        UserKnownHostsFile=/dev/null
        StrictHostKeyChecking no
        LogLevel quiet
        ControlMaster auto
        IdentityFile C:\Users\YourUser\.ssh/codespaces.auto
```

### 4. Connect via Antigravity IDE
Open the Antigravity IDE (or your preferred editor) and connect using the Host alias you just added to your SSH config.
- **Host:** The name following `Host` in the config block (e.g., `cs.<codespace_code>.main`).
- **User:** `codespace`.

### 5. Navigate to Workspace
Once connected to the remote machine, navigate to the project workspace:
```bash
cd /workspaces/ai-dev-tools-zoomcamp
```
