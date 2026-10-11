---
name: omni-tune
description: >-
  Audits the current workspace and uses the omni-agents CLI to inspect, recommend,
  configure, synchronize, or remove skills, subagents, and rules across AI coding tools.
  Use when the user asks to tune the project, configure AI tools with omni-agents,
  needs smart recommendations for skills or agents, or wants to remove and clean configurations.
---

# omni-tune

Autonomous workspace tuning and lifecycle management powered by the `omni-agents` CLI.
Works with any AI assistant (Google Antigravity, Cursor, Claude Code, GitHub Copilot, Universal, etc.).

## 1. Binary Resolution Precedence

Before running commands, determine which CLI execution method is available:

1. **System Binary (Primary)**:
   If `omni-agents` or the shorthand `omni` is available in the system `PATH` (installed via `uv tool`, `pipx`, or installer scripts):
   ```bash
   omni-agents --info
   # or
   omni --info
   ```
2. **Local Repository Mode (Fallback)**:
   When running directly inside the cloned `omni-agents` repository where global binaries are not yet installed in `PATH`:
   ```bash
   python -m omni_agents.cli --info
   # or with active virtual environment:
   .venv/Scripts/python.exe -m omni_agents.cli --info
   ```

*Note: In the examples below, `<omni>` refers to whichever binary command is active (`omni-agents`, `omni`, or `python -m omni_agents.cli`).*

---

## 2. Multi-Tool Target Detection

`omni-agents` compiles configs into native formats for multiple AI assistants. Check what the workspace currently uses or ask if unclear:

| AI Assistant | Target ID | Detected Files / Directories |
| :--- | :--- | :--- |
| Google Antigravity | `antigravity` | `.agents/`, `~/.gemini/config/` |
| Cursor IDE | `cursor` | `.cursor/rules/*.mdc` |
| Claude Code | `claude` | `CLAUDE.md`, `~/.claude/CLAUDE.md` |
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` |
| Universal Standard | `universal` | `AGENTS.md` |
| Kiro | `kiro` | `.kiro/`, `AGENTS.md` |
| OpenCode | `opencode` | `.opencode/`, `AGENTS.md` |
| Codex (OpenAI) | `codex` | `AGENTS.md` |
| All Tools (Team) | `all` | Configures all active/supported tools simultaneously |

---

## 3. The Prescriptive Consultant (Solving User Indecision)

When the developer asks for recommendations or is unsure what skills and agents to install:

1. **Silently Inspect the Project**: Check manifest files in the repository root:
   - Python: `pyproject.toml`, `requirements.txt`, `Pipfile`
   - Node/TypeScript: `package.json`, `tsconfig.json`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
   - Svelte/SvelteKit: `svelte.config.js`
2. **Do NOT Dump 30+ Raw Options**: Present a concise **Gold Standard (Prescriptive Default)**:
   - **Recommended Rules**: (e.g. `general` or `pt-br-dev`)
   - **Recommended Skills**: 2 to 3 core skills tailored to the stack
   - **Recommended Subagents**: (e.g. `code-reviewer`)
   - **Optional Add-ons**: 1 or 2 situational items (e.g. `security-auditor` if auth/API routes are present)
3. **Decisive Execution**:
   - If the user confirms or says "apply what you think is best", execute immediately with `--sync -y`.

---

## 4. Operational Workflows

Always include `-y` (or `--yes`) and `--sync` in automated runs to bypass interactive prompts and prevent blocking.

### A. Discover Available Components
```bash
<omni> --list-tools
<omni> --list-agents
<omni> --list-rules
<omni> --list-skills
```

### B. Configure and Synchronize Workspace
Apply components to the current workspace (`.`):
```bash
# Specific tool:
<omni> . --tools antigravity --skills coding-standards,researching-codebases --agents code-reviewer --rules general --sync -y

# Multi-tool setup (e.g. Antigravity + Cursor):
<omni> . --tools antigravity,cursor --skills coding-standards --agents code-reviewer --sync -y

# Apply to all tools:
<omni> . --tools all --skills coding-standards --rules general --sync -y
```

### C. Remove and Clean Workspace
```bash
# Clean a single tool:
<omni> . --clean --tools cursor

# Clean all generated AI configs from workspace:
<omni> . --clean --tools all

# Deactivate specific component type:
<omni> . --tools antigravity --agents none --sync -y
<omni> . --tools antigravity --skills none --sync -y
```

### D. Central Workspaces & Inspection
Inspect and manage tracked workspaces configured with omni-agents across your machine:
```bash
# List all tracked workspaces across your system:
<omni> --list-workspaces

# Diagnostics and system path information:
<omni> --info
```

### E. Remote Extensions & External Community Skills
```bash
# List installed extensions:
<omni> --ext-list

# Install remote extension from official catalog:
<omni> --ext-install agents/security-auditor.md
<omni> --ext-install skills/stacks/svelte5

# Install external community skill or agent from Git/GitHub repository:
<omni> add https://github.com/blader/humanizer --skill humanizer
# or shorthand:
<omni> --ext-add blader/humanizer

# Check for updates without modifying files (status table):
<omni> --ext-check

# Update extensions (interactive confirmation or automated with -y):
<omni> --ext-update -y

# Remove extension:
<omni> --ext-remove <extension-key>
```

---

## 5. Further Reference

For exhaustive CLI flags, parameter reference, and diagnostics options, see [references/cli-reference.md](references/cli-reference.md).
