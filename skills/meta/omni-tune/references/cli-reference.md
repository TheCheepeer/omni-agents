# omni-agents CLI Reference

Complete exhaustive command-line interface documentation for `omni-agents`.

## 1. Invocation Syntax

```bash
<omni> [TARGET_PATH] [OPTIONS]
```

Where `<omni>` can be:
- `omni-agents` (Canonical binary in system PATH)
- `omni` (Shorthand alias in system PATH)
- `python -m omni_agents.cli` (Local repository execution)

---

## 2. Arguments & Options Matrix

### Positional Arguments

| Argument | Description | Default |
| :--- | :--- | :--- |
| `target` | Path to target project repository directory | Current working directory (`.`) |

### Component Selection (Inline Workspace Tuning)

| Flag | Short | Value Syntax | Description |
| :--- | :--- | :--- | :--- |
| `--tool`, `--tools` | `-t` | `<tool1,tool2>` or `all` | Target tool adapter(s): `antigravity`, `claude`, `cursor`, `copilot`, `universal`, `kiro`, `opencode`, `codex`, `all`. |
| `--agent`, `--agents` | `-a` | `<id1,id2>` or `all`, `none` | Subagent ID(s) to activate in workspace. |
| `--rule`, `--rules` | `-r` | `<id1,id2>` or `all`, `none` | Rule profile ID(s) to apply (e.g. `general`, `pt-br-dev`). |
| `--skill`, `--skills` | `-s` | `<id1,id2>` or `all`, `none` | Skill ID(s) or categories to activate in workspace. |
| `--global` | | *(flag)* | Targets global user tool configuration directories (`~/.gemini/config`, `~/.claude`) instead of workspace folders. |

### Operational Modes

| Flag | Short | Description |
| :--- | :--- | :--- |
| `--sync` | | Executes fast headless synchronization without launching interactive TUI menus. |
| `--clean` | | Removes configurations and unlinks generated files for specified tool(s) (or all tools). |
| `--yes` | `-y` | Automatically answers yes to confirmation prompts (e.g. replacing existing junctions or links). |
| `--update` | | Explicitly checks for newer releases and executes self-upgrade via pip or git pull. |
| `--no-update-check` | | Suppresses automatic background update check upon CLI startup. |

### Discovery & Catalog Listing

| Flag | Description |
| :--- | :--- |
| `--list-tools` | Lists all supported AI coding tool adapters and exits. |
| `--list-agents` | Lists available subagents with descriptions and exits. |
| `--list-rules` | Lists available rule profiles with descriptions and exits. |
| `--list-skills` | Lists available modular skills grouped by category and exits. |

### Remote Extensions Management

| Flag | Argument | Description |
| :--- | :--- | :--- |
| `--ext-list` | *(none)* | Lists installed remote extensions and exits. |
| `--ext-install` | `<ITEM>` | Installs a remote extension from catalog (e.g. `agents/code-reviewer.md` or `skills/stacks/svelte5`). Alias: `--ext-download`. |
| `--ext-update` | *(none)* | Checks and updates all installed remote extensions. |
| `--ext-remove` | `<KEY>` | Removes an installed remote extension by key. |

### Diagnostics & Configuration

| Flag | Argument | Description |
| :--- | :--- | :--- |
| `--info` | *(none)* | Displays runtime diagnostics: active directories, execution mode (`repo` vs `documents`), catalog repo, version. |
| `--open-folder` | *(none)* | Opens personal `Documents/omni-agents` folder in desktop file manager, or prints path in headless environments. |
| `--lang` | `<CODE>` | Sets UI language explicitly (e.g. `en`, `pt`, `pt-BR`, `es`). |
| `-h`, `--help` | *(none)* | Displays CLI usage syntax, flag descriptions, and examples. |

---

## 3. Supported Target Tools & Output Locations

| Target Tool | Tool ID | Workspace Output Destination | Global Output Destination |
| :--- | :--- | :--- | :--- |
| Google Antigravity | `antigravity` | `.agents/` (`skills.json`, `rules/`, `agents/`) | `~/.gemini/config/` (`skills/`, `rules/`, `agents/`) |
| Claude Code | `claude` | `CLAUDE.md` in workspace root | `~/.claude/CLAUDE.md` |
| Cursor IDE | `cursor` | `.cursor/rules/*.mdc` | N/A (Workspace only) |
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` | N/A (Workspace only) |
| Universal | `universal` | `AGENTS.md` in workspace root | N/A (Workspace only) |
| Kiro | `kiro` | `AGENTS.md` and `.kiro/` | N/A (Workspace only) |
| OpenCode | `opencode` | `AGENTS.md` and `.opencode/` | N/A (Workspace only) |
| Codex (OpenAI) | `codex` | `AGENTS.md` tailored for Codex | N/A (Workspace only) |
