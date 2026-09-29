#!/usr/bin/env python3
"""
Language selection menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.i18n import (
    get_available_languages,
    get_language_badge,
    get_language_name,
    resolve_language_code,
    t,
)
from omni_agents.targets import save_workspace_state
from omni_agents.tui.common import clear_screen


def handle_language_selection(
    repo_root: Path,
    target_path: Path | None,
    current_lang: str,
    app_config: dict[str, Any],
    workspace_state: dict[str, Any],
    omni_docs_dir: Path | None = None,
) -> str:
    """Interactively allows user to toggle or choose UI language and persists it in config.json."""
    available_langs = get_available_languages()
    current_code = resolve_language_code(current_lang)

    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('lang_selection_title', current_code)}")
    print("=" * 65)

    for idx, l_desc in enumerate(available_langs, 1):
        code = l_desc["code"]
        name = l_desc["name"]
        default_tag = " (default)" if code == "en" else ""
        active_tag = " *" if code == current_code else ""
        print(f"  [{idx}] {name}{default_tag}{active_tag}")

    print("\n" + "-" * 65)
    curr_badge = get_language_badge(current_code)
    print(f"  {t('lang_toggle_hint', current_code, current=curr_badge)}")
    print(f"  {t('lang_cancel_hint', current_code)}")
    print("-" * 65)

    try:
        choice = input(f"\n{t('choose_option', current_code)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return current_code

    if choice in ("v", "voltar", "volver"):
        return current_code

    if choice == "":
        codes = [l["code"] for l in available_langs]
        if current_code in codes:
            idx = (codes.index(current_code) + 1) % len(codes)
            new_lang = codes[idx]
        else:
            new_lang = codes[0] if codes else "en"
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available_langs):
            new_lang = available_langs[idx]["code"]
        else:
            return current_code
    else:
        new_lang = resolve_language_code(choice)
        if new_lang == "en" and choice not in (
            "en",
            "english",
            "ingles",
            "inglês",
            "1",
        ):
            return current_code

    app_config["language"] = new_lang
    save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)

    if target_path:
        workspace_state["language"] = new_lang
        save_workspace_state(target_path, workspace_state)

    lang_name = get_language_name(new_lang)
    print(f"\n[OK] {t('lang_saved', new_lang, name=lang_name, lang=lang_name)}")
    try:
        input(f"\n{t('press_enter', new_lang)}")
    except (EOFError, KeyboardInterrupt):
        pass

    return new_lang
