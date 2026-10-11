# Architecture & Technical Design

This document details the internal architecture, design principles, component resolution layers, filesystem strategies, and target adapter patterns used in `omni-agents`.

---

## 1. High-Level Architecture Overview

`omni-agents` functions as a cross-platform synchronization and distribution hub for AI coding agent configurations. It translates and maps a single, standardized set of skills, rules, and subagents into the respective formats and directory structures required by various AI developer tools (Antigravity, Cursor, Claude Code, GitHub Copilot, Universal, etc.).

```
+-------------------------------------------------------------------------------+
|                             omni-agents CLI                                  |
|         (Entry points: `omni-agents` and `omni` console scripts)              |
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         v                                                         v
+-----------------------------+                           +-----------------------------+
|    Runtime Environment      |                           |     Storage Resolution      |
|    - CLI Arguments & TUI    |                           |     - Documents/omni-agents/|
|    - i18n Localization      |                           |     - Local Dev (Repo)      |
|    - Update & Sync Engine   |                           |     - Bundled Package       |
+-----------------------------+                           +-----------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                      Layered Component Resolution Engine                      |
|                                                                               |
|   Priority 1: custom/  (User overrides in Documents/omni-agents/custom/)      |
|   Priority 2: ext/     (Third-party remote packages in ext/<package>/)        |
|   Priority 3: bundled/ (Core skills, rules, subagents in repo / package)      |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                            Target Adapter Layer                               |
|                       (scripts.targets.base.TargetConfigurator)               |
|                                                                               |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
|   |  Antigravity  |  |    Cursor     |  |    Claude     |  |    Copilot    |  |
|   +---------------+  +---------------+  +---------------+  +---------------+  |
+-------------------------------------------------------------------------------+
                                      |
                                      v
+-------------------------------------------------------------------------------+
|                           Filesystem Link Engine                              |
|   - Directory Junctions (Windows without admin privileges)                   |
|   - Symbolic Links (POSIX / Unix / macOS)                                     |
|   - Hard Links / Copying (Fallback with omni-manifest.json tracking)          |
+-------------------------------------------------------------------------------+
```

---

## 2. Layered Storage Resolution

To allow users to install `omni-agents` globally without modifying repository files or losing custom personal additions across updates, the CLI uses a layered resolution architecture managed by `src/omni_agents/env_paths.py`.

### Storage Hierarchy

When resolving skills, rules, or subagents, the resolution engine inspects components in the following order:

1. **Custom Layer (`Documents/omni-agents/custom/`)**:
    - Holds user-authored components that are private or unique to the user machine.
    - Takes precedence over any remote or bundled components with the same name.
    - Preserved across tool updates and catalog synchronization.

2. **Extensions Layer (`Documents/omni-agents/ext/`)**:
    - Holds external repositories and packages downloaded via remote sync, official catalog, or community Git repositories (`omni add <url>`).
    - Structured as `ext/skills/<category>/<skill_id>/`, `ext/agents/*.md`, and `ext/rules/<profile>/`.
    - Takes precedence over bundled core items.

3. **Core / Bundled Layer**:
    - In local development mode: loaded directly from the repository root (`rules/`, `skills/`, `subagents/`).
    - In global package mode: loaded from the distributed package data or the synced remote cache.

### Execution Modes

The CLI automatically detects its execution context via `get_execution_mode()` in `src/omni_agents/env_paths.py`:

- **Local Dev Mode (`repo`)**: Active when running directly inside the cloned `omni-agents` repository containing `.git`.
- **User Space Mode (`documents`)**: Active when installed via pip or global installers. Configurations and extensions are read from and written to `~/Documents/omni-agents/`.

---

## 3. Filesystem Linking Engine

Different operating systems and developer environments have varying permissions and filesystem capabilities. `omni-agents` uses a resilient linking engine with automated fallbacks to ensure changes made in central configurations reflect immediately in workspaces without manual copying whenever possible.

### Strategy by Operating System

| Operating System   | Directory Strategy                                     | File Strategy                | Admin / Elevation Required                                    |
| :----------------- | :----------------------------------------------------- | :--------------------------- | :------------------------------------------------------------ |
| **Windows**        | NTFS Directory Junction (`os.system('mklink /J ...')`) | Physical copy / hardlink     | **No** (Junctions do not require Developer Mode or elevation) |
| **Linux / macOS**  | Symbolic Link (`os.symlink`)                           | Symbolic Link (`os.symlink`) | **No**                                                        |
| **Fallback (Any)** | Recursive Directory Copy                               | File Copy                    | **No**                                                        |

### Link Preservation, Replacement & Junction Handling

- On Windows, directory junctions report as directories rather than symlinks under older APIs. The filesystem routines in `scripts/targets/base.py` explicitly identify reparse points (`FILE_ATTRIBUTE_REPARSE_POINT = 0x400`) and symlinks, safely unbinding them via `os.rmdir()` or `path.unlink()` without deleting real target data.
- **Target Inspection & Broken Link Repair**: `get_link_target()` inspects the link destination via `os.readlink()`. If an existing link points to a deleted directory (`is_link_broken()`), or points to a different installation/clone, `omni-agents` warns the user and prompts for confirmation before safely replacing the link (or automatically with `-y` / `--yes`).
- When physical copying is selected or required, an `omni-manifest.json` file is generated inside the target configuration directory. During cleanup or synchronization, only files registered in the manifest are removed or overwritten, safeguarding user modifications.

---

## 4. Target Adapter Pattern

All supported AI coding tools inherit from the abstract base class `BaseTarget` defined in `src/omni_agents/targets/base.py`.

```python
class BaseTarget(ABC):
    target_id: str
    display_name: str
    description: str
    supports_global: bool = False

    @abstractmethod
    def configure_workspace(
        self,
        target_path: Path,
        repo_root: Path,
        scanned: dict[str, Any],
        agents: list[dict[str, Any]],
        rules: list[dict[str, Any]],
        skills_by_cat: dict[str, set[str]],
        lang: str = "en",
    ) -> bool:
        pass

    @abstractmethod
    def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
        pass
```

### Supported Target Adapters

1. **Antigravity (`src/omni_agents/targets/antigravity.py`)**:
    - Workspace destination: `.agents/`
    - Subagents: `.agents/agents/*.md`
    - Rules: `.agents/rules/*.md`
    - Skills: `.agents/skills.json` declarative manifest
    - Driver: Bundles `omni-tune` as mandatory built-in skill

2. **Cursor (`src/omni_agents/targets/cursor.py`)**:
    - Workspace destination: `.cursor/rules/*.mdc`
    - Rules & metadata: Formatted with `globs` and `alwaysApply` frontmatter

3. **Claude Code (`src/omni_agents/targets/claude.py`)**:
    - Workspace destination: `CLAUDE.md` in project root
    - Skills: Integrated into `.claude/skills/`

4. **GitHub Copilot (`src/omni_agents/targets/copilot.py`)**:
    - Workspace destination: `.github/copilot-instructions.md`
    - Rules & guidelines: Consolidated project instructions

5. **Universal Ecosystem (`src/omni_agents/targets/universal.py`)**:
    - **Universal**: `AGENTS.md` in workspace root
    - **Kiro**: `AGENTS.md` and `.kiro/steering/`
    - **OpenCode**: `AGENTS.md` and `.opencode/rules/`
    - **Codex**: `AGENTS.md` optimized for OpenAI Codex

### Central Workspace Registry

To track all configured repositories across the machine, `omni-agents` maintains a registry at `~/Documents/omni-agents/workspaces.json`. Whenever a workspace is synchronized or cleaned, its entry is automatically registered or updated. Users can list all tracked workspaces via `omni-agents --list-workspaces` or switch between them directly in the interactive TUI via `[w]`.

---

## 5. Security & Isolation

- **Zero Credential Exposure**: `omni-agents` never handles, stores, or commits API tokens, private keys, or passwords.
- **Path Sanitization**: All incoming workspace and extension paths are normalized using `Path.resolve()` to prevent path traversal attacks (`../` escapement).
- **Offline Resilience**: If GitHub or network connectivity is unavailable, update checks and remote catalog sync operations fail gracefully, allowing the CLI to function entirely offline using local caches.
