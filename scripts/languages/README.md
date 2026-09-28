# Internationalization (i18n) Catalogs

This directory contains localized translation catalogs for the `omni-agent` CLI and TUI orchestrator (`configure_workspace.py`).

## File Structure

Each language is declared in its own JSON file (e.g., `en.json`, `pt.json`, `es.json`).

```json
{
  "_meta": {
    "code": "es",
    "name": "Español",
    "badge": "ES",
    "aliases": ["es", "spanish", "espanol", "español"]
  },
  "ui": {
    "app_title": "CONFIGURADOR MULTI-TOOL...",
    ...
  },
  "targets": {
    "dir_not_link": "El directorio existente no es un enlace: {dst}",
    ...
  },
  "target_descriptions": {
    "antigravity": {
      "display_name": "Google Antigravity",
      "description": "Configuración vía .agents/ (workspace) y ~/.gemini/config/ (global)"
    },
    ...
  }
}
```

## Adding a New Language

1. Copy `en.json` to `<code_or_locale>.json` (for example, `es.json` or `fr.json`).
2. Update the `_meta` section with the language code, full display name, badge acronym, and any CLI aliases.
3. Translate the strings in the `ui`, `targets`, and `target_descriptions` sections.
4. The system will automatically detect the new file on launch without requiring code modifications.
