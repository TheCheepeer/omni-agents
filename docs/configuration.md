# Configuration & Extensions Guide

This guide explains how `omni-agents` handles user configuration files, remote catalog synchronization, third-party extensions, and self-update mechanisms.

---

## 1. Configuration File (`config.json`)

`omni-agents` creates and maintains a global configuration file located at:

- **Windows**: `C:\Users\<User>\Documents\omni-agents\config.json`
- **Linux / macOS**: `~/Documents/omni-agents/config.json`

If running directly inside a cloned git repository (Local Dev Mode), a local `config.json` in the repository root takes precedence if present.

### Configuration Schema

```json
{
    "repository_url": "https://github.com/TheCheepeer/omni-agents",
    "default_language": "en",
    "auto_update_check": true,
    "links_mode": "auto",
    "enabled_targets": [
        "antigravity",
        "cursor",
        "claude",
        "copilot",
        "universal"
    ]
}
```

### Parameter Reference

| Key                 | Type            | Default                                        | Description                                                                                     |
| :------------------ | :-------------- | :--------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| `repository_url`    | `string`        | `"https://github.com/TheCheepeer/omni-agents"` | Base GitHub repository used for fetching remote component updates and catalog metadata.         |
| `default_language`  | `string`        | `"en"`                                         | Default language for UI prompts and messages (`en`, `pt`, `es`).                                |
| `auto_update_check` | `boolean`       | `true`                                         | When `true`, queries GitHub releases or PyPI periodically to notify the user of newer versions. |
| `links_mode`        | `string`        | `"auto"`                                       | Strategy for linking files to targets (`"auto"`, `"junction"`, `"symlink"`, `"copy"`).          |
| `enabled_targets`   | `array[string]` | All targets                                    | List of target adapter names visible in the interactive menu.                                   |

### Workspace-Scoped State (`.agents/workspace_state.json`)

Target tool selections and synchronized configurations are strictly isolated per workspace rather than globally in `config.json`. Each project repository maintains its own state file:

```json
{
  "tools_configured": true,
  "active_targets": [
    "antigravity",
    "cursor"
  ],
  "selected_agents": [],
  "selected_rules": [],
  "selected_skills": {}
}
```

- **First-Run Prompt**: When navigating to an unconfigured workspace for the first time, `omni-agents` prompts the user to select tools for that workspace.
- **Strict Isolation**: Selections made in Project A never leak into Project B.
- **Persistence**: Selections remain in `.agents/workspace_state.json` until modified via `[t]` or removed via `[c]`.

---

## 2. Directory Layout & Custom Overrides

The primary workspace inside `Documents/omni-agents/` is structured as follows:

```text
Documents/omni-agents/
|-- config.json           # User configuration
|-- custom/               # Personal overrides (highest priority)
|   |-- rules/            # Custom user rules
|   |-- skills/           # Custom user skills
|   `-- subagents/        # Custom user subagents
|-- ext/                  # Installed extensions & community packages
|   |-- package-a/
|   `-- package-b/
`-- cache/                # Downloaded catalogs & version cache
```

### Creating Custom Skills & Rules

Any rule profile placed inside `Documents/omni-agents/custom/rules/<profile>/AGENTS.md` (or custom skills in `custom/skills/<category>/<skill>/SKILL.md`) is automatically discovered by `omni-agents`. If a custom rule shares the same profile name as a core or extension rule, the **custom rule always takes precedence**.

---

## 3. Remote Catalog Sync & Extensions

Managed by `src/omni_agents/remote_sync.py`, `omni-agents` can fetch and inspect remote component packages hosted on GitHub:

```python
from omni_agents.remote_sync import fetch_remote_tree, check_all_extensions_updates
```

### Extension Installation

Extensions downloaded from the official catalog or external Git repositories are placed into `Documents/omni-agents/ext/`.

- **Official Catalog**: Installed via `omni-agents --ext-install <component_path>` (e.g. `skills/stacks/svelte5`).
- **External Community Skills**: Installed directly from Git/GitHub repositories via:
  ```bash
  omni add https://github.com/blader/humanizer --skill humanizer
  # or shorthand:
  omni --ext-add blader/humanizer
  ```
- **Manifest Tracking**: Origin metadata is saved in `Documents/omni-agents/ext/manifest.json` (recording `source_url`, `branch`, `sha`, `installed_at`, and install command).
- **Checking Updates (`--ext-check`)**: Queries the latest remote commit without downloading the entire repository, outputting a clear status table.
- **Applying Updates (`--ext-update`)**: Prompts for interactive confirmation (`[y/N]`) before updating installed extensions, or automatically with `-y` / `--yes`.
- Extensions are mapped with precedence order: `custom/` > `ext/` > `bundled/`.

### Resilient Offline Mode

If network access is unavailable or GitHub API rate limits are encountered:

1. `omni-agents` logs a non-blocking diagnostic notice.
2. The CLI falls back immediately to existing local configurations in `custom/`, `ext/`, and bundled packages.
3. Operations continue without interruption or blocking network timeouts.

---

## 4. Automatic Update & Self-Upgrade Engine

The self-update engine (`src/omni_agents/updater.py`) keeps `omni-agents` up to date across execution modes:

### Upgrade Execution Flow

```text
omni-agents --update
         |
         v
Check execution mode?
         |
         +--> Git Repository: Executes `git pull --ff-only`
         |
         `--> Pip / Standalone: Executes `python -m pip install --upgrade omni-agents-cli`
```

### Version Check Suppression

In automated environments, CI/CD pipelines, or isolated environments, the startup version check can be disabled either by passing `--no-update-check` or setting `"auto_update_check": false` in `config.json`.
