# Contributing & Development Standards

Thank you for contributing to `omni-agents`! This guide explains how to set up your local development environment, adhere to project coding and architectural conventions, add new tool adapters, and extend multilingual localizations.

---

## 1. Development Setup

### Requirements

- **Python**: `>=3.10` (Tested up to `3.13.x`).
- **Git**: Installed and available in your `PATH`.

### Clone & Environment Setup
 
Clone the repository and set up an isolated virtual environment (`.venv`) so your global Python remains clean:
 
```bash
git clone https://github.com/TheCheepeer/omni-agents.git
cd omni-agents

# 1. Create and activate a local virtual environment
# Windows:
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies and local package in editable mode
pip install -r requirements.txt
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

All tool adapters reside in `src/omni_agents/targets/` and subclass `BaseTarget` from `src/omni_agents/targets/base.py`.

### Step-by-Step Implementation

1. **Create the Adapter File**:
   Create a new file in `src/omni_agents/targets/<tool_name>.py`:

    ```python
    from pathlib import Path
    from typing import Any
    from omni_agents.targets.base import BaseTarget

    class MyNewToolTarget(BaseTarget):
        target_id = "mynewtool"
        display_name = "My New Tool (.mynewtool)"
        description = "Generates instructions in .mynewtool/"
        supports_global = False

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
            # Implement workspace configuration logic here
            return True

        def clean_workspace(self, target_path: Path, lang: str = "en") -> bool:
            # Implement workspace cleanup logic here
            return True
    ```

2. **Register the Adapter**:
   Import and register your class in `TARGET_REGISTRY` in `src/omni_agents/targets/__init__.py`.

3. **Add Target Descriptions**:
   Add the tool's display name and description in all 3 language catalogs (`en.json`, `pt.json`, `es.json`) under `target_descriptions`.

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
