# omni-agent

> [Leia em Portugues / Read in Brazilian Portuguese](README.pt-BR.md)

A centralized, tool-agnostic hub to version, manage, and distribute specialized subagents, development rules, and modular skill libraries across multiple AI coding assistants.

---

## Supported Tools

`omni-agent` unifies context management and compiles directly into the native format expected by each assistant:

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
omni-agent/
├── agents/                          # Specialized subagent personas
│   ├── accessibility-reviewer.md
│   ├── code-reviewer.md
│   └── security-auditor.md
├── rules/                           # Global engineering rules and guidelines
│   └── AGENTS.md
├── scripts/                         # Automation configurator and target adapters
│   ├── configure_workspace.py       # Interactive TUI and CLI orchestrator
│   ├── i18n.py                      # Decoupled internationalization engine
│   ├── languages/                   # Localized translation catalogs (en.json, pt.json...)
│   └── targets/                     # Specialized target adapter modules
│       ├── __init__.py              # Central target registry
│       ├── base.py                  # Adapter contracts and filesystem utilities
│       ├── antigravity.py           # Google Antigravity adapter
│       ├── claude.py                # Claude Code adapter (CLAUDE.md)
│       ├── cursor.py                # Cursor IDE adapter (.cursor/rules/*.mdc)
│       ├── copilot.py               # GitHub Copilot adapter
│       └── universal.py             # Universal, Kiro, OpenCode, and Codex adapter
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
└── README.md
```

---

## Contents

### 1. Subagents (`agents/`)

- `accessibility-reviewer.md`: Digital accessibility (a11y) specialist covering WCAG 2.1/2.2 (A, AA, AAA) and WAI-ARIA guidelines.
- `code-reviewer.md`: Static code analysis, Clean Code, readability, and solid architecture reviewer.
- `security-auditor.md`: Application security specialist covering OWASP Top 10 and secure coding practices.

### 2. Global Rules (`rules/`)

- `AGENTS.md`: High-priority guidelines covering software architecture, security, communication standards, strict emoji prohibition, and modern Tailwind CSS standards.

### 3. Modular Skill Library (`skills/`)

To optimize token consumption and prevent model choice hesitation:

1. **Global Core (`skills/global/`):** 5 essential skills establishing foundational pair-programming behavior across any project (~800 tokens total).
2. **On-Demand Library (`skills/{planning,docs,frontend,meta,stacks}/`):** Specialized skills selectively mounted only in relevant repositories.

---

## Cross-Platform Configuration & Automation

The [`scripts/configure_workspace.py`](scripts/configure_workspace.py) script runs natively on **Windows, Linux, and macOS** using only the Python standard library (zero external dependencies).

### 1. Interactive Mode (TUI / GUI)

```bash
# Launch interactive menu:
python scripts/configure_workspace.py

# Or specify target project directory directly:
python scripts/configure_workspace.py /path/to/project
python scripts/configure_workspace.py .
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
python scripts/configure_workspace.py --list-tools

# Synchronize workspace across all active tools:
python scripts/configure_workspace.py /path/to/project --sync

# Configure for a specific tool:
python scripts/configure_workspace.py /path/to/project --tool cursor --sync
python scripts/configure_workspace.py /path/to/project --tool claude --sync
python scripts/configure_workspace.py /path/to/project --tool copilot --sync

# Configure for all tools simultaneously (Multi-Tool):
python scripts/configure_workspace.py /path/to/project --tool all --sync

# Remove configuration for a single tool without affecting others:
python scripts/configure_workspace.py /path/to/project --tool cursor --clean
python scripts/configure_workspace.py /path/to/project --clean  # Remove all

# Apply global machine configuration:
python scripts/configure_workspace.py --global
python scripts/configure_workspace.py --tool claude --global

# Force UI language:
python scripts/configure_workspace.py --lang en
python scripts/configure_workspace.py --lang pt
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

## License

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
