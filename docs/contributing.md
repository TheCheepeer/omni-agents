# Contributing & Development Standards

Thank you for contributing to `omni-agents`! This guide explains how to set up your local development environment, adhere to project coding and architectural conventions, add new tool adapters, and extend multilingual localizations.

---

## 1. Development Setup

### Requirements

- **Python**: `>=3.10` (Tested up to `3.13.x`).
- **Git**: Installed and available in your `PATH`.

### Clone & Editable Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/TheCheepeer/omni-agents.git
cd omni-agents

# Install editable CLI entry points (omni-agents and omni)
pip install -e .
```

Verify your active environment:

```bash
omni-agents --info
```

---

## 2. Core Engineering Standards

### English-Only Code & Comments

- All code identifiers, docstrings, and inline comments must be written in **English**.
- User-facing terminal strings must not be hardcoded in Python files; instead, reference localized keys via the `t("key")` helper from `scripts.i18n`.

### Absolute Prohibition of Emojis

- **Never use emojis** in code comments, docstrings, terminal outputs, commits, pull request titles, or documentation files. Maintain a clean, professional, and strictly textual presentation across the entire codebase.

### Typing & Modern Python Practices

- Use native union types introduced in PEP 604 (e.g., `str | Path`, `list[str] | set[str]`).
- Do not use legacy `typing.Union` or `typing.Optional` unless required for runtime introspection.
- Avoid blind exception handling (`except Exception: pass`). Use explicit exception types or `contextlib.suppress(OSError, FileNotFoundError)`.

---

## 3. Adding a New Target Adapter

All tool adapters reside in `scripts/targets/` and subclass `TargetConfigurator` from `scripts/targets/base.py`.

### Step-by-Step Implementation

1. **Create the Adapter File**:
   Create a new file in `scripts/targets/<tool_name>.py`:

    ```python
    from pathlib import Path
    from scripts.targets.base import TargetConfigurator

    class MyNewToolConfigurator(TargetConfigurator):
        name = "mynewtool"
        display_name = "My New Tool (.mynewtool)"
        target_dir_name = ".mynewtool"

        def configure(
            self,
            workspace_root: str | Path,
            selected_rules: list[str] | set[str] | None = None,
            selected_skills: list[str] | set[str] | None = None,
            selected_subagents: list[str] | set[str] | None = None,
            global_mode: bool = False,
            link_mode: str = "auto",
        ) -> bool:
            target_dir = self.resolve_target_dir(workspace_root, global_mode)
            # Implement configuration and linking logic here
            return True

        def clean(self, workspace_root: str | Path, global_mode: bool = False) -> bool:
            target_dir = self.resolve_target_dir(workspace_root, global_mode)
            # Implement cleanup logic here
            return True
    ```

2. **Register the Adapter**:
   Import and register your class in `TARGET_REGISTRY` in `src/omni_agents/targets/__init__.py`.

3. **Validate Linking**:
   Ensure directory junctions are used on Windows and symbolic links on Unix/macOS, falling back to physical copy with an `omni-manifest.json` file.

---

## 4. Multilingual Internationalization (i18n)

All user messages are localized across English (`en`), Brazilian Portuguese (`pt`), and Spanish (`es`).

### Localization Workflow

1. **Add Keys to JSON Catalogs**:
   Add identical keys across all three catalogs in `src/omni_agents/languages/`:
    - `src/omni_agents/languages/en.json` (Canonical reference)
    - `src/omni_agents/languages/pt.json`
    - `src/omni_agents/languages/es.json`

2. **Retrieve Strings via `t()`**:
   In Python files, import `t` from `omni_agents.i18n`:

    ```python
    from omni_agents.i18n import t

    print(t("my_new_message_key", count=5))
    ```

3. **Interactive Control Synonyms**:
   If adding interactive prompts, ensure keyboard shortcuts and word synonyms are mapped for all three languages in `src/omni_agents/tui/`.

---

## 5. Testing & Verification

Before submitting changes, run the automated test suite and check Python compilation:

```bash
# Run unit test suite
python -m unittest discover -s tests -p "test_*.py" -v

# Verify Python bytecode compilation across src
python -m compileall src
```

# Verify CLI commands and help outputs

omni-agents --help
omni-agents --info
omni-agents --list-tools

```

```
