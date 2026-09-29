# omni-agents

> Translations: [Português](docs/translations/README.pt-BR.md) | [Español](docs/translations/README.es.md)

A centralized, tool-agnostic hub to version, manage, and distribute specialized subagents, development rules, and modular skill libraries across multiple AI coding assistants.

---

## Supported Tools

`omni-agents` unifies context management and compiles directly into the native format expected by each assistant:

| Tool                   | Target ID     | Scope              | Generated Files & Destinations                                          |
| :--------------------- | :------------ | :----------------- | :---------------------------------------------------------------------- |
| **Google Antigravity** | `antigravity` | Global + Workspace | `.agents/` (`skills.json`, `rules/`, `agents/`) and `~/.gemini/config/` |
| **Claude Code**        | `claude`      | Global + Workspace | `CLAUDE.md` in project root and `~/.claude/CLAUDE.md`                   |
| **Cursor IDE**         | `cursor`      | Workspace          | `.cursor/rules/*.mdc` (with `globs` and `alwaysApply` metadata)         |
| **GitHub Copilot**     | `copilot`     | Workspace          | Consolidated `.github/copilot-instructions.md`                          |
| **Universal**          | `universal`   | Workspace          | Standardized `AGENTS.md` in project root                                |
| **Kiro**               | `kiro`        | Workspace          | Root `AGENTS.md` and `.kiro/` directory                                 |
| **OpenCode**           | `opencode`    | Workspace          | Root `AGENTS.md` and `.opencode/` directory                             |
| **Codex (OpenAI)**     | `codex`       | Workspace          | Root `AGENTS.md` tailored for Codex                                     |

---

## Repository Structure

```text
omni-agents/
├── agents/                          # Specialized subagent personas
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Modular rule profiles (one AGENTS.md per folder)
│   ├── general/                     # General engineering guidelines (English)
│   │   └── AGENTS.md
│   └── pt-br-dev/                   # Brazilian Portuguese development guidelines
│       └── AGENTS.md
├── src/                                 # Application source package (Src Layout)
│   └── omni_agents/                     # Main CLI package
│       ├── cli.py                       # CLI entry point, argument parsing & dispatch
│       ├── core/                        # Core domain logic (scanner, linker, config)
│       ├── tui/                         # Interactive terminal UI menus
│       ├── commands/                    # Headless CLI command handlers
│       ├── i18n.py                      # Decoupled internationalization engine
│       ├── languages/                   # Localized translation catalogs (en.json, pt.json...)
│       └── targets/                     # Specialized target adapter modules
│           ├── __init__.py              # Central target registry
│           ├── base.py                  # Adapter contracts and filesystem utilities
│           ├── antigravity.py           # Google Antigravity adapter
│           ├── claude.py                # Claude Code adapter (CLAUDE.md)
│           ├── cursor.py                # Cursor IDE adapter (.cursor/rules/*.mdc)
│           ├── copilot.py               # GitHub Copilot adapter
│           └── universal.py             # Universal, Kiro, OpenCode, and Codex adapter
├── tests/                               # Automated unit test suite
├── skills/
│   ├── global/                      # GLOBAL CORE (~800 tokens) - Essential for all projects
│   │   ├── coding-standards/        # Technical excellence, Clean Code, and engineering patterns
│   │   ├── comunicacao-clara/       # Clear, unpacked communication and concise synthesis
│   │   ├── grug-brained-dev/        # Anti-overengineering and simplicity mindset
│   │   ├── reducing-entropy/        # Combating technical debt and deleting dead code
│   │   └── researching-codebases/   # Multi-agent codebase research and navigation
│   ├── planning/                    # LIBRARY: Planning, auditing, and roadmaps
│   ├── docs/                        # LIBRARY: Technical writing and documentation
│   ├── frontend/                    # LIBRARY: UI design, visual standards, and Tailwind CSS
│   ├── meta/                        # LIBRARY: Prompt engineering and customization authoring
│   └── stacks/                      # LIBRARY: Frameworks, languages, and infrastructure
├── docs/
│   └── translations/                # Translated documentation
│       ├── README.pt-BR.md
│       └── README.es.md
└── README.md                        # Primary documentation in English
```

---

## Contents

### 1. Subagents (`agents/`)

- `accessibility-reviewer.md`: Digital accessibility (a11y) specialist covering WCAG 2.1/2.2 (A, AA, AAA) and WAI-ARIA guidelines.
- `code-reviewer.md`: Static code analysis, Clean Code, readability, and solid architecture reviewer.
- `security-auditor.md`: Application security specialist covering OWASP Top 10 and secure coding practices.

### 2. Rule Profiles (`rules/`)

Organized into dedicated profile folders, each containing its own `AGENTS.md` contract:

- `pt-br-dev/AGENTS.md`: Engineering guidelines, security standards, Brazilian Portuguese communication rules, strict accentuation, emoji prohibition, and Tailwind CSS.
- `general/AGENTS.md`: Universal guidelines for international projects in English, clean architecture, security, and modern frontend practices.

### 3. Modular Skill Library (`skills/`)

To optimize token consumption and prevent model choice hesitation:

1. **Global Core (`skills/global/`):** 5 essential skills establishing foundational pair-programming behavior across any project (~800 tokens total).
2. **On-Demand Library (`skills/{planning,docs,frontend,meta,stacks}/`):** Specialized skills selectively mounted only in relevant repositories.

---

## Installation

The official and standard way to install `omni-agents` is via **`pip`**:

```bash
pip install omni-agents-cli
```

To upgrade to the latest version at any time:
```bash
pip install --upgrade omni-agents-cli
```

Once installed, the `omni-agents` (and shorthand `omni`) commands are available globally in your terminal.

---

### Alternative Installation Methods

If you prefer isolated CLI environments or automated one-line scripts:

#### Alternative 1: Isolated Environment via `pipx`

`pipx` installs CLI tools in dedicated virtual environments and exposes them directly to your `PATH`.

1. **Install `pipx` (if not already installed):**
   - **Windows (PowerShell):**
     ```powershell
     python -m pip install --user pipx
     python -m pipx ensurepath
     ```
     *(Restart your terminal after running `ensurepath`).*
   - **Linux (Ubuntu / Debian):**
     ```bash
     sudo apt update && sudo apt install -y pipx
     pipx ensurepath
     ```
     *(Fedora: `sudo dnf install pipx` | Arch Linux: `sudo pacman -S python-pipx`)*
   - **macOS:**
     ```bash
     brew install pipx
     pipx ensurepath
     ```

2. **Install `omni-agents`:**
   ```bash
   pipx install omni-agents-cli
   ```
   To upgrade: `pipx upgrade omni-agents-cli`

#### Alternative 2: High-Performance via `uv`

If you use `uv`, you can install `omni-agents` as an isolated global tool:

```bash
uv tool install omni-agents-cli
```
To upgrade: `uv tool upgrade omni-agents-cli`

#### Alternative 3: One-Line Convenience Scripts

- **Windows (PowerShell):**
  ```powershell
  irm https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.ps1 | iex
  ```
- **Linux / macOS:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/TheCheepeer/omni-agents/main/install.sh | bash
  ```

---

## Cross-Platform Configuration & Automation

The tool can be executed globally via the **`omni-agents`** command (or shorthand alias `omni`).

When working in the cloned repository during development, install in editable mode:

```bash
pip install -e .
```

### 1. Interactive Mode (TUI / GUI)

```bash
# Launch interactive menu globally:
omni-agents
# or shorthand:
omni

# Or specify target project directory directly:
omni-agents /path/to/project
omni-agents .
```

#### Interactive Menu Layout:

```text
=================================================================
  MULTI-TOOL AGENT, RULES & SKILLS CONFIGURATOR
=================================================================
  Target Workspace:   [/path/to/project]
  Active Tools:       antigravity, cursor, claude
-----------------------------------------------------------------
  [t] Select Target Tools (Antigravity, Cursor, Claude...)
  [1] Global Machine Configuration (Antigravity & Claude)
  [2] Subagents for Workspace
  [3] Rules for Workspace
  [4] Modular Skills for Workspace
  [s] Synchronize All (Sync active tools in batch)
  [c] Clean / Uninstall by Tool
  [l] Language / Idioma: [EN | PT-BR]
  [5] Exit
-----------------------------------------------------------------
  [w] Set / Change Target Workspace
=================================================================
```

---

### 2. Command-Line Interface (CLI / Automation)

Execute commands directly within scripts or CI/CD pipelines:

```bash
# List all supported tools:
omni-agents --list-tools

# Synchronize workspace across all active tools:
omni-agents /path/to/project --sync

# Configure for a specific tool:
omni-agents /path/to/project --tool cursor --sync
omni-agents /path/to/project --tool claude --sync
omni-agents /path/to/project --tool copilot --sync

# Configure for all tools simultaneously (Multi-Tool):
omni-agents /path/to/project --tool all --sync

# Remove configuration for a single tool without affecting others:
omni-agents /path/to/project --tool cursor --clean
omni-agents /path/to/project --clean  # Remove all

# Apply global machine configuration:
omni-agents --global
omni-agents --tool claude --global

# Force UI language:
omni-agents --lang en
omni-agents --lang pt
```

---

### 3. Strategic Scenarios

#### Multi-Tool Team Workflow

In teams where different developers use different environments (e.g., developer A uses Cursor, developer B uses VS Code with Copilot, and developer C uses Antigravity), use `--tool all`. The script exports native configuration files for each assistant from a single source of truth, guaranteeing project-wide consistency.

#### Fast Synchronization (Sync)

When updating rules or skills in this repository, run `--sync` on any target project to instantly regenerate consolidated files (`CLAUDE.md`, `copilot-instructions.md`, `.cursor/rules/`, etc.).

#### State Persistence

Workspace preferences are saved in `.agents/workspace_state.json` (automatically added to `.gitignore`), allowing you to inspect and modify active targets at any time.

---

## Documentation

For in-depth technical documentation and developer guides, consult:

- [Architecture & Design](docs/architecture.md): Layered component resolution, filesystem linking engine, and target adapter patterns.
- [CLI Reference](docs/cli.md): Complete command-line syntax, flags, interactive TUI navigation, and headless/CI automation.
- [Configuration & Extensions](docs/configuration.md): Schema for `config.json`, personal overrides in `custom/`, remote catalog syncing, and updater.
- [Contributing Standards](docs/contributing.md): Local environment setup, engineering guidelines, adding new target adapters, and localization.

---

## Credits and Acknowledgements

Several skills included in this repository were adapted from:

- [agent-skills](https://github.com/joshuadavidthomas/agent-skills) by Josh Thomas (MIT License).
- [The Grug Brained Developer](https://grugbrain.dev/) by Colin McDonnell.
- [Diátaxis Documentation Framework](https://diataxis.fr/) by Daniele Procida.

See the [NOTICE](NOTICE) file for formal third-party license and copyright declarations.

---

## License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
