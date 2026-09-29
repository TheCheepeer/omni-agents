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
```

When run without arguments, `omni-agents` detects the current working directory as the target workspace and opens an interactive Terminal User Interface (TUI). When executed with operational flags like `--sync` or `--clean`, it runs headlessly without user intervention.

---

## 2. Command Options

### Target & Tool Selection

| Option          | Shorthand    | Description                                                                                          |
| :-------------- | :----------- | :--------------------------------------------------------------------------------------------------- |
| `target`        | _Positional_ | Target project directory path (default: current working directory `.`).                              |
| `--tool <name>` | `-t <name>`  | Specifies target tool adapter (`antigravity`, `cursor`, `claude`, `copilot`, `universal`, or `all`). |
| `--global`      | _(none)_     | Targets global user tool configurations rather than workspace project folders.                       |
| `--rule <id>`   | `-r <id>`    | Specifies rule profile to apply (e.g. `pt-br-dev`, `general`).                                       |

### Operational Modes

| Option              | Description                                                                                                                                |
| :------------------ | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `--sync`            | Fast synchronization mode: applies selected components immediately without opening the interactive menu. Ideal for CI/CD or setup scripts. |
| `--clean`           | Unbinds and removes configurations for the specified tool (or all tools) from the workspace.                                               |
| `--update`          | Explicitly checks for newer releases and executes self-upgrade via pip or git pull.                                                        |
| `--no-update-check` | Suppresses automatic background update check upon CLI startup.                                                                             |

### Diagnostics & Information

| Option               | Description                                                                                             |
| :------------------- | :------------------------------------------------------------------------------------------------------ |
| `--info`             | Outputs detailed runtime diagnostics (version, active directories, execution mode, catalog repository). |
| `--list-tools`       | Lists all supported AI coding tool adapters and exits.                                                  |
| `--lang <code/name>` | Sets UI language explicitly (e.g. `en`, `pt`, `pt-BR`, `es`, `english`, `portugues`, `espanol`).        |
| `-h`, `--help`       | Displays command syntax, flag descriptions, and usage examples.                                         |

---

## 3. Interactive TUI Navigation

When launched interactively, `omni-agents` presents a localized menu:

```text
============================================================
  omni-agents: Multi-Tool Agent Configurator (v1.0.0)
  Target: /path/to/my-project
============================================================

Supported AI Assistants:
  1. Antigravity (.gemini)
  2. Cursor (.cursor)
  3. Claude Code (.claude)
  4. GitHub Copilot (.github)
  5. Universal (.agents)
  6. All Tools
  0. Exit
```

### Multilingual Control Synonyms

The menu supports commands and shortcuts in English, Portuguese, and Spanish:

| Action             | English                  | Portuguese                        | Spanish                           |
| :----------------- | :----------------------- | :-------------------------------- | :-------------------------------- |
| **Confirm & Save** | `save`, `s`, `enter`     | `salvar`, `guardar`, `s`, `enter` | `guardar`, `salvar`, `g`, `enter` |
| **Go Back**        | `back`, `b`              | `voltar`, `v`                     | `volver`, `atras`, `v`            |
| **Clear / Clean**  | `clean`, `clear`, `c`    | `limpar`, `l`                     | `limpiar`, `l`                    |
| **Exit**           | `exit`, `quit`, `q`, `0` | `sair`, `q`, `0`                  | `salir`, `q`, `0`                 |
| **Select All**     | `all`, `a`               | `todos`, `t`                      | `todos`, `t`                      |

---

## 4. Headless & CI/CD Examples

### Automated Workspace Setup

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
