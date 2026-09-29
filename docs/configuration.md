# Configuration & Extensions Guide

This guide explains how `omni-agents` handles user configuration files, remote catalog synchronization, third-party extensions, and self-update mechanisms.

---

## 1. Configuration File (`config.json`)

`omni-agents` creates and maintains a global configuration file located at:

- **Windows**: `C:\Users\<User>\Documents\omni-agent\config.json`
- **Linux / macOS**: `~/Documents/omni-agent/config.json`

If running directly inside a cloned git repository (Local Dev Mode), a local `config.json` in the repository root takes precedence if present.

### Configuration Schema

```json
{
    "repository_url": "https://github.com/TheCheepeer/omni-agent",
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

| Key                 | Type            | Default                                       | Description                                                                                     |
| :------------------ | :-------------- | :-------------------------------------------- | :---------------------------------------------------------------------------------------------- |
| `repository_url`    | `string`        | `"https://github.com/TheCheepeer/omni-agent"` | Base GitHub repository used for fetching remote component updates and catalog metadata.         |
| `default_language`  | `string`        | `"en"`                                        | Default language for UI prompts and messages (`en`, `pt`, `es`).                                |
| `auto_update_check` | `boolean`       | `true`                                        | When `true`, queries GitHub releases or PyPI periodically to notify the user of newer versions. |
| `links_mode`        | `string`        | `"auto"`                                      | Strategy for linking files to targets (`"auto"`, `"junction"`, `"symlink"`, `"copy"`).          |
| `enabled_targets`   | `array[string]` | All targets                                   | List of target adapter names visible in the interactive menu.                                   |

---

## 2. Directory Layout & Custom Overrides

The primary workspace inside `Documents/omni-agent/` is structured as follows:

```text
Documents/omni-agent/
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

Any rule profile placed inside `Documents/omni-agent/custom/rules/<profile>/AGENTS.md` (or custom skills in `custom/skills/<category>/<skill>/SKILL.md`) is automatically discovered by `omni-agents`. If a custom rule shares the same profile name as a core or extension rule, the **custom rule always takes precedence**.

---

## 3. Remote Catalog Sync & Extensions

Managed by `scripts/remote_sync.py`, `omni-agents` can fetch and inspect remote component packages hosted on GitHub:

```python
from scripts.remote_sync import RemoteCatalogSync

syncer = RemoteCatalogSync(repo_url="https://github.com/TheCheepeer/omni-agent")
catalog = syncer.fetch_catalog()
```

### Extension Installation

Third-party extensions downloaded from community repositories are placed into `Documents/omni-agent/ext/<package_name>/`.

- Each extension can contribute rules, skills, or subagents.
- Extensions are mapped with precedence order: `custom/` > `ext/<package>/` > `bundled/`.
- If an extension requires specific tools, its metadata is parsed and registered in the active session.

### Resilient Offline Mode

If network access is unavailable or GitHub API rate limits are encountered:

1. `omni-agents` logs a non-blocking diagnostic notice.
2. The CLI falls back immediately to existing local configurations in `custom/`, `ext/`, and bundled packages.
3. Operations continue without interruption or blocking network timeouts.

---

## 4. Automatic Update & Self-Upgrade Engine

The self-update engine (`scripts/updater.py`) keeps `omni-agents` up to date across execution modes:

### Upgrade Execution Flow

```text
omni-agents --update
         |
         v
Check execution mode?
         |
         +--> Git Repository: Executes `git pull --ff-only`
         |
         `--> Pip / Standalone: Executes `python -m pip install --upgrade omni-agents`
```

### Version Check Suppression

In automated environments, CI/CD pipelines, or isolated environments, the startup version check can be disabled either by passing `--no-update-check` or setting `"auto_update_check": false` in `config.json`.
