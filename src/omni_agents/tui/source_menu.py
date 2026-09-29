#!/usr/bin/env python3
"""
Source layer selection menu for omni-agents TUI.
Allows selecting component origin (repository, extensions, custom, or merged).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen


def select_component_source(
    component_type: str,
    sources: dict[str, Any],
    is_dev: bool,
    omni_docs_dir: Path | None,
    target_path: Path | None = None,
    lang: str = "en",
) -> dict[str, Any] | None:
    """
    Submenu for selecting component origin (ext, custom, or all; plus repo in dev mode).
    If the chosen folder is empty, warns the user clearly with instructions on where to
    download (via option [e]) or place custom files (via option [o]).
    """
    type_label_map = {
        "agents": t("menu_agents", lang).lstrip("[0123456789] ").strip(),
        "rules": t("menu_rules", lang).lstrip("[0123456789] ").strip(),
        "skills": t("menu_skills", lang).lstrip("[0123456789] ").strip(),
    }
    type_display = type_label_map.get(component_type, component_type)

    def _get_count(layer_key: str) -> int:
        data = sources.get(layer_key, {})
        if component_type == "agents":
            return len(data.get("agents", []))
        if component_type == "rules":
            return len(data.get("rules", []))
        if component_type == "skills":
            skills_cat = data.get("skills_by_category", {})
            return sum(len(v) for v in skills_cat.values())
        return 0

    repo_count = _get_count("repo")
    ext_count = _get_count("ext")
    custom_count = _get_count("custom")
    all_count = _get_count("merged")

    custom_subpath = (
        (omni_docs_dir / "custom" / component_type)
        if omni_docs_dir
        else Path.home() / "Documents" / "omni-agents" / "custom" / component_type
    )

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('source_menu_title', lang, type=type_display)}")
        print("=" * 65)
        if target_path:
            print(f"  {t('target_workspace', lang)}: {target_path}")
        print("-" * 65)

        if is_dev:
            print(
                f"  {t('source_layer_repo', lang, type=component_type, count=repo_count)}"
            )
            print(
                f"  {t('source_layer_ext_dev', lang, type=component_type, count=ext_count)}"
            )
            print(
                f"  {t('source_layer_custom_dev', lang, type=component_type, count=custom_count)}"
            )
            print(f"  {t('source_layer_all_dev', lang, count=all_count)}")
        else:
            print(
                f"  {t('source_layer_ext', lang, type=component_type, count=ext_count)}"
            )
            print(
                f"  {t('source_layer_custom', lang, type=component_type, count=custom_count)}"
            )
            print(f"  {t('source_layer_all', lang, count=all_count)}")

        print(f"  {t('ext_menu_back', lang)}")
        print("-" * 65)

        try:
            choice = input(f"\n{t('choose_option', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None

        if choice in ("v", "voltar", "volver", "back", "q", "exit"):
            return None

        selected_layer = None
        if is_dev:
            if choice == "1":
                selected_layer = "repo"
            elif choice == "2":
                selected_layer = "ext"
            elif choice == "3":
                selected_layer = "custom"
            elif choice in ("4", "all", "todos", "todas"):
                selected_layer = "merged"
        else:
            if choice == "1":
                selected_layer = "ext"
            elif choice == "2":
                selected_layer = "custom"
            elif choice in ("3", "all", "todos", "todas"):
                selected_layer = "merged"

        if not selected_layer:
            print(f"[!] {t('invalid_option', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            continue

        layer_count = _get_count(selected_layer)
        if layer_count == 0:
            clear_screen()
            print("\n" + "=" * 65)
            print(f"  {type_display.upper()}")
            print("=" * 65)
            if selected_layer == "ext":
                print(f"\n[!] {t('source_empty_ext', lang, type=component_type)}")
            elif selected_layer == "custom":
                print(
                    f"\n[!] {t('source_empty_custom', lang, type=component_type, path=custom_subpath)}"
                )
            elif selected_layer == "merged":
                print(f"\n[!] {t('source_empty_all', lang, type=component_type)}")
            else:
                fallback_key = (
                    "no_agents_found"
                    if component_type == "agents"
                    else "no_rules_found"
                    if component_type == "rules"
                    else "no_skills_found"
                )
                print(f"\n[!] {t(fallback_key, lang)}")
            try:
                input(f"\n{t('press_enter_menu', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
            continue

        return sources[selected_layer]
