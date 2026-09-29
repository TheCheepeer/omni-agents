#!/usr/bin/env python3
"""
Source layer selection menu for omni-agents TUI.
Allows selecting component origin (repository, extensions, custom, or merged).
Rendered using modern action cards and item count badges.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen
from omni_agents.tui.theme import (
    COLOR_MUTED,
    COLOR_PRIMARY,
    COLOR_SUCCESS,
    Panel,
    Table,
    box,
    console,
    escape,
    get_styled_choice,
    press_enter_to_continue,
    render_banner,
)


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

        table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
        table.add_column("Key", style=f"bold {COLOR_PRIMARY}", width=6, justify="right")
        table.add_column("Layer", style="bold white", width=26)
        table.add_column("Count", width=16)

        if is_dev:
            table.add_row(
                "[1]",
                t("source_layer_repo_name", lang),
                f"[bold {COLOR_SUCCESS}]● {repo_count} {t('items_count', lang)}[/bold {COLOR_SUCCESS}]",
            )
            table.add_row(
                "[2]",
                t("source_layer_ext_name", lang),
                f"[{COLOR_MUTED}]● {ext_count} {t('items_count', lang)}[/{COLOR_MUTED}]",
            )
            table.add_row(
                "[3]",
                t("source_layer_custom_name", lang),
                f"[{COLOR_MUTED}]● {custom_count} {t('items_count', lang)}[/{COLOR_MUTED}]",
            )
            table.add_row(
                "[4]",
                t("source_layer_merged_name", lang),
                f"[bold {COLOR_PRIMARY}]● {all_count} {t('items_count', lang)} ({t('recommended', lang)})[/bold {COLOR_PRIMARY}]",
            )
        else:
            table.add_row(
                "[1]",
                t("source_layer_ext_name", lang),
                f"[{COLOR_MUTED}]● {ext_count} {t('items_count', lang)}[/{COLOR_MUTED}]",
            )
            table.add_row(
                "[2]",
                t("source_layer_custom_name", lang),
                f"[{COLOR_MUTED}]● {custom_count} {t('items_count', lang)}[/{COLOR_MUTED}]",
            )
            table.add_row(
                "[3]",
                t("source_layer_merged_name", lang),
                f"[bold {COLOR_PRIMARY}]● {all_count} {t('items_count', lang)} ({t('recommended', lang)})[/bold {COLOR_PRIMARY}]",
            )

        table.add_row("[v]", t("ext_menu_back", lang), "")

        panel = Panel(
            table,
            title=f"[bold white]{escape(t('source_menu_title', lang, type=type_display))}[/bold white]",
            title_align="left",
            subtitle=f"[{COLOR_MUTED}]{escape(str(target_path) if target_path else '')}[/{COLOR_MUTED}]",
            subtitle_align="right",
            box=box.ROUNDED,
            border_style="dim cyan",
            padding=(1, 1),
        )
        console.print(panel)

        choice = get_styled_choice(t("choose_option", lang))

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
            render_banner(t("invalid_option", lang), level="warning")
            press_enter_to_continue(t("press_enter", lang))
            continue

        layer_count = _get_count(selected_layer)
        if layer_count == 0:
            clear_screen()
            if selected_layer == "ext":
                render_banner(
                    t("source_empty_ext", lang, type=component_type), level="warning"
                )
            elif selected_layer == "custom":
                render_banner(
                    t(
                        "source_empty_custom",
                        lang,
                        type=component_type,
                        path=custom_subpath,
                    ),
                    level="warning",
                )
            elif selected_layer == "merged":
                render_banner(
                    t("source_empty_all", lang, type=component_type), level="warning"
                )
            else:
                fallback_key = (
                    "no_agents_found"
                    if component_type == "agents"
                    else "no_rules_found"
                    if component_type == "rules"
                    else "no_skills_found"
                )
                render_banner(t(fallback_key, lang), level="warning")

            press_enter_to_continue(t("press_enter_menu", lang))
            continue

        return sources[selected_layer]
