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
| `--global`        | _(none)_     | Targets global user tool configurations (`~/.gemini`, `~/.claude`) rather than workspace project folders.      |

### Operational Modes

| Option              | Shorthand | Description                                                                                                                                |
| :------------------ | :-------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `--sync`            | _(none)_  | Fast synchronization mode: applies selected components immediately without opening the interactive menu. Ideal for CI/CD or setup scripts. |
| `--clean`           | _(none)_  | Unbinds and removes configurations for the specified tool(s) (or all tools) from the workspace (or global with `--global`).                |
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
=================================================================
  MULTI-TOOL AGENT, RULES & SKILLS CONFIGURATOR (v1.0.0)
=================================================================
  Mode:             Local Dev Mode (Repository)
  Target Workspace: /path/to/my-project
  Active Tools:     Google Antigravity
-----------------------------------------------------------------
  [t] Select Target Tools (Antigravity, Cursor, Claude...)
  [1] Install Agents & Skills Globally (Antigravity & Claude)
  [2] Subagents for Workspace
  [3] Rules (Workspace vs Global)
  [4] Modular Skills for Workspace
  [e] Remote Extensions (GitHub Catalog / ext/)
  [o] Open Personal Folder in File Explorer (Documents/omni-agents)
  [s] Synchronize All (Sync active tools in batch)
  [c] Clean / Uninstall by Tool
  [l] Language / Idioma: [EN]
  [5] Exit
-----------------------------------------------------------------
  [w] Set / Change Target Workspace
=================================================================
```

### Multilingual Control Synonyms

The menu supports commands and shortcuts in English, Portuguese, and Spanish:

| Action                          | English                  | Portuguese                        | Spanish                            |
| :------------------------------ | :----------------------- | :-------------------------------- | :--------------------------------- |
| **Confirm & Save**              | `save`, `s`, `enter`     | `salvar`, `guardar`, `s`, `enter` | `guardar`, `salvar`, `g`, `enter`  |
| **Go Back**                     | `back`, `b`              | `voltar`, `v`                     | `volver`, `atras`, `v`             |
| **Clear / Clean**               | `clean`, `clear`, `c`    | `limpar`, `l`                     | `limpiar`, `l`                     |
| **Exit**                        | `exit`, `quit`, `q`, `0` | `sair`, `q`, `0`                  | `salir`, `q`, `0`                  |
| **Select All**                  | `all`, `a`               | `todos`, `t`                      | `todos`, `t`                       |
| **Open / Show Personal Folder** | `open`, `custom`, `o`    | `abrir`, `pessoal`, `custom`, `o` | `abrir`, `personal`, `custom`, `o` |

### Rules Configuration: Workspace (Local) vs Global (Machine-wide)

Option `[3] Rules (Workspace vs Global)` provides an interactive screen where users explicitly select or desmarcar rules for either scope:

- **Rules are not automatically linked to Global**: When global tools (such as Antigravity or Claude) are configured, rules are **never** bound globally unless explicitly chosen by the user.
- **Visual Current Status**: The screen displays what is currently active in Workspace (Local) and in Global (Machine), plus a warning if a legacy automatic whole-directory link is detected.
- **Granular Toggle & Desmarcar Commands**:
    - `w<num>`: Toggle rule selection in Workspace (e.g. `w1`, `w2`)
    - `g<num>`: Toggle rule selection in Global (e.g. `g1`, `g2`)
    - `<num>`: Toggle rule in Workspace (shortcut)
    - `all-w` / `all-g`: Mark all rules in Workspace / Global
    - `clean-w`: Desmarcar all rules from Workspace (removes project rules)
    - `clean-g`: Desmarcar all rules from Global (removes machine-wide rules)
    - `clean-all`: Desmarcar all rules from both Workspace and Global
    - `s` / `salvar`: Persist and apply rule selections immediately

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

### Global User Configuration

Link configurations to global user tool directories across all installed assistants:

```bash
omni-agents --global --tool all --sync
```

Link a specific rule profile globally with automatic overwrite confirmation:

```bash
omni-agents --global --tool antigravity --rule pt-br-dev -y
```

> **Smart Link Replacement & Broken Link Repair**:
> When linking global directories (such as Antigravity `agents`, `skills`, or `rules`), `omni-agents` automatically inspects existing directory junctions and symbolic links:
>
> - **Same Target**: If a link already points to the requested source directory, no changes or prompts are made.
> - **Different Target**: If an existing link points to another directory (e.g. switching between an installed copy in `Documents/omni-agents` and a local development clone, or switching rule profiles), `omni-agents` displays the current path and asks for confirmation before replacing it.
> - **Broken / Dangling Link**: If an existing link points to a nonexistent directory (e.g. after moving or deleting an older clone), `omni-agents` detects the broken link and offers to repair and repoint it.
> - **Physical Directory**: If a real directory already exists at the destination, it is safely backed up with a `.backup` suffix before creating the link.

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
