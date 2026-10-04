# CLI Reference & Usage Guide

`omni-agents` provides a command-line interface available globally under two command aliases:

- `omni-agents` (Canonical binary name)
- `omni` (Shorthand alias)

---

## 1. Syntax & Overview

```bash
omni-agents [TARGET_PATH] [OPTIONS]
# or
omni [TARGET_PATH] [OPTIONS]
# or
python -m omni_agents [TARGET_PATH] [OPTIONS]
```

When run without arguments, `omni-agents` automatically detects the current working directory as the target workspace and opens an interactive Terminal User Interface (TUI). When executed with operational flags like `--sync` or `--clean`, it runs headlessly without user intervention.

> **Default / System Directory Protection**: If `omni-agents` is launched from a default shell home directory (such as `C:\Users\<username>` in Windows PowerShell, `/home/<username>` in Linux, or `/Users/<username>` in macOS) or drive roots (`C:\`, `/`), it displays a warning banner and prompts to select a project workspace. In non-interactive CLI mode, it requests confirmation before applying changes to home directories, unless `-y` / `--yes` is passed.

---

## 2. Command Options

### Target & Component Selection (Inline Workspace Tuning)

| Option            | Shorthand    | Description                                                                                                    |
| :---------------- | :----------- | :------------------------------------------------------------------------------------------------------------- |
| `target`          | _Positional_ | Target project directory path (default: current working directory `.`).                                        |
| `--tools <list>`  | `-t <list>`  | Target tool adapter(s), comma-separated (`antigravity`, `cursor`, `claude`, `copilot`, `universal`, or `all`). |
| `--agents <list>` | `-a <list>`  | Subagent ID(s) to activate, comma-separated (e.g. `code-reviewer,security-auditor`, or `all`, `none`).         |
| `--rules <list>`  | `-r <list>`  | Rule profile(s) to apply, comma-separated (e.g. `general,pt-br-dev`, or `all`, `none`).                        |
| `--skills <list>` | `-s <list>`  | Skill ID(s) or categories to activate (e.g. `testing,git/commit-helper`, or `all`, `none`).                    |
| `--global`        | `-g`         | Legacy global flag (deprecated in v1.0.3; used with `--clean` to unlink legacy machine-wide junctions/symlinks).|

### Operational Modes

| Option              | Shorthand | Description                                                                                                                                |
| :------------------ | :-------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `--sync`            | _(none)_  | Fast synchronization mode: applies selected components immediately without opening the interactive menu. Ideal for CI/CD or setup scripts. |
| `--clean`           | _(none)_  | Unbinds and removes configurations for the specified tool(s) (or all tools) from the workspace.                                             |
| `--yes`             | `-y`      | Automatically answers yes to confirmation prompts (e.g. replacing existing links or repairing broken links).                               |
| `--update`          | _(none)_  | Explicitly checks for newer releases and executes self-upgrade via pip or git pull.                                                        |
| `--no-update-check` | _(none)_  | Suppresses automatic background update check upon CLI startup.                                                                             |

### Discovery, Extensions & Diagnostics

| Option                 | Description                                                                                                  |
| :--------------------- | :----------------------------------------------------------------------------------------------------------- |
| `--list-tools`         | Lists all supported AI coding tool adapters and exits.                                                       |
| `--list-agents`        | Lists all available subagents with descriptions and exits.                                                   |
| `--list-rules`         | Lists all available rule profiles with descriptions and exits.                                               |
| `--list-skills`        | Lists all available modular skills grouped by category and exits.                                            |
| `--list-workspaces`    | Lists all tracked workspace projects across your system and exits.                                           |
| `--ext-list`           | Lists all remote extensions currently installed in `Documents/omni-agents/ext` and exits.                    |
| `--ext-install <item>` | Installs a remote extension from GitHub catalog (e.g. `agents/code-reviewer.md` or `skills/testing/pytest`). |
| `--ext-update`         | Checks and updates all installed remote extensions.                                                          |
| `--ext-remove <key>`   | Removes an installed remote extension by key.                                                                |
| `--open-folder`        | Opens personal `Documents/omni-agents` folder in File Explorer (or displays path in headless mode).          |
| `--info`               | Outputs detailed runtime diagnostics (version, active directories, execution mode, catalog repository).      |
| `--lang <code/name>`   | Sets UI language explicitly (e.g. `en`, `pt`, `pt-BR`, `es`, `english`, `portugues`, `espanol`).             |
| `-h`, `--help`         | Displays command syntax, flag descriptions, and usage examples.                                              |

---

## 3. Interactive TUI Navigation

When launched interactively, `omni-agents` presents a localized menu:

```text
┌─ OMNI-AGENTS v1.0.3 ────────────────────────────────────────────────────────┐
│                                                                             │
│  Target Workspace      /path/to/my-project                                  │
│  Active Tools          ● antigravity, cursor                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
┌─ Context Actions ───────────────────────────────────────────────────────────┐
│                                                                             │
│       [t]  Target Tools                  Select active AI tools             │
│       [1]  Subagents                     Specialized agent personas         │
│       [2]  Workspace Rules               Architecture rules & standards     │
│       [3]  Modular Skills                Modular library (stacks, docs...)  │
│       [e]  Remote Extensions             Remote catalog & community packages│
│       [o]  Personal Folder               Open custom components folder      │
│       [s]  Synchronize All               Compile and apply to active tools  │
│       [c]  Clean Workspace               Remove generated files & links     │
│       [l]  Language                      Cycle UI language: [EN]            │
│       [w]  Workspaces                    Switch recent project workspace    │
│       [q]  Exit                          Quit configurator                  │
│                                                                             │
└───────────────────────────────────────────── Type shortcut key or 'q' to quit ─┘
```

### Multilingual Control Synonyms

The menu supports commands and shortcuts in English, Portuguese, and Spanish:

| Action                          | English                  | Portuguese                        | Spanish                            |
| :------------------------------ | :----------------------- | :-------------------------------- | :--------------------------------- |
| **Confirm & Save**              | `save`, `s`, `enter`     | `salvar`, `guardar`, `s`, `enter` | `guardar`, `salvar`, `g`, `enter`  |
| **Go Back**                     | `back`, `b`, `v`         | `voltar`, `v`                     | `volver`, `atras`, `v`             |
| **Clear / Clean**               | `clean`, `clear`, `c`    | `limpar`, `l`                     | `limpiar`, `l`                     |
| **Exit**                        | `exit`, `quit`, `q`      | `sair`, `q`                       | `salir`, `q`                       |
| **Select All**                  | `all`, `a`               | `todos`, `t`                      | `todos`, `t`                       |
| **Open / Show Personal Folder** | `open`, `custom`, `o`    | `abrir`, `pessoal`, `custom`, `o` | `abrir`, `personal`, `custom`, `o` |

### Rules Configuration for Workspace

Option `[2] Workspace Rules` provides an interactive screen where users select which architecture guidelines and rule profiles apply to the project:

- **100% Workspace-Scoped**: Rules are applied directly to the active project folder (e.g. `.agents/rules/`, `.cursor/rules/`, `CLAUDE.md`, or `AGENTS.md`).
- **Granular Toggle & Commands**:
    - `<num>`: Toggle rule selection in workspace
    - `all`: Select all available rules
    - `clean`: Uncheck all rules from workspace
    - `s` / `save`: Persist and apply rule selections immediately
    - `v` / `back`: Return to main menu without changes

> **Desktop vs Headless Environment Detection**:
> When accessing the personal folder (`[o]`), `omni-agents` automatically detects whether a graphical display environment is available. On desktop systems, it opens the operating system's default file manager at `Documents/omni-agents/`. On headless environments (e.g., remote SSH sessions, CI/CD runners, or containers), it outputs the absolute directory path directly to stdout without attempting to launch desktop processes.

---

## 4. Autonomous Agent Tuning & Headless CI/CD Examples

### Autonomous Agent Self-Tuning in a Project

An autonomous AI agent running in a repository can inspect, select, and configure its tools, subagents, rules, and skills without opening an interactive TUI:

```bash
# 1. Discover available components
omni-agents --list-tools
omni-agents --list-agents
omni-agents --list-rules
omni-agents --list-skills

# 2. Tune the workspace with required subagents, rules, and skills
omni-agents . --tools antigravity,cursor \
  --agents code-reviewer,security-auditor \
  --rules general,pt-br-dev \
  --skills testing,global/coding-standards \
  --sync

# 3. Download an official extension directly if needed
omni-agents --ext-install agents/accessibility-reviewer.md

# 4. Clean up configurations for a specific tool
omni-agents . --clean --tool cursor
```

### Automated Workspace Setup (Batch Sync)

Apply all rules, skills, and subagents for Cursor in the current project:

```bash
omni-agents . --tool cursor --sync
```

Configure both Antigravity and Universal targets for a specific repository:

```bash
omni-agents /var/www/my-api --tool antigravity --sync
omni-agents /var/www/my-api --tool universal --sync
```

### Central Workspace Management

Track and inspect all workspaces configured with omni-agents across your machine:

```bash
# List all active workspaces tracked across your machine:
omni-agents --list-workspaces
```

### Legacy Global Migration (v1.0.3)

In v1.0.3, `omni-agents` automatically scans and unlinks legacy global directory junctions (`~/.gemini/config/agents`, `~/.gemini/config/skills`, `~/.gemini/config/rules`, and `~/.claude/CLAUDE.md`) left by previous versions (v1.0.2). You can also trigger global cleanup explicitly:

```bash
omni-agents --global --clean
```

### Workspace Cleanup

Safely remove linked agent configurations from a project:

```bash
omni-agents /path/to/project --clean --tool all
```

### Diagnostic Inspection

Inspect resolution directories, active execution mode, and configured repository:

```bash
omni-agents --info
```
