#!/usr/bin/env python3
"""
Language selection menu for omni-agents TUI.
Rendered using styled language cards and active status badges.
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

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column(t("table_col_index", current_code), style="dim", width=6, justify="right")
    table.add_column(t("table_col_name", current_code), style="bold white", width=22)
    table.add_column(t("table_col_badge", current_code), width=10)
    table.add_column(t("table_col_status", current_code), width=18)

    for idx, l_desc in enumerate(available_langs, 1):
        code = l_desc["code"]
        name = l_desc["name"]
        badge = l_desc.get("badge", code.upper())
        is_active = code == current_code

        status_markup = (
            f"[bold {COLOR_SUCCESS}]● {t('status_active', current_code)}[/bold {COLOR_SUCCESS}]"
            if is_active
            else f"[{COLOR_MUTED}]○ {t('status_available', current_code)}[/{COLOR_MUTED}]"
        )
        badge_markup = f"[bold {COLOR_PRIMARY}]\\[{escape(badge)}][/bold {COLOR_PRIMARY}]"

        table.add_row(
            escape(f"[{idx}]"),
            escape(name),
            badge_markup,
            status_markup,
        )

    curr_badge = get_language_badge(current_code)
    hint_text = t("lang_toggle_hint", current_code, current=curr_badge)

    panel = Panel(
        table,
        title=f"[bold white]{escape(t('lang_selection_title', current_code))}[/bold white]",
        title_align="left",
        subtitle=f"[{COLOR_MUTED}]{escape(hint_text)}[/{COLOR_MUTED}]",
        subtitle_align="right",
        box=box.ROUNDED,
        border_style="dim cyan",
        padding=(1, 1),
    )
    console.print(panel)

    cancel_panel = Panel(
        f"[{COLOR_MUTED}]{escape(t('lang_cancel_hint', current_code))}[/{COLOR_MUTED}]",
        box=box.ROUNDED,
        border_style="dim",
        padding=(0, 1),
    )
    console.print(cancel_panel)

    choice = get_styled_choice(t("choose_option", current_code))

    if choice in ("v", "voltar", "volver", "q"):
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
    render_banner(
        t("lang_saved", new_lang, name=lang_name, lang=lang_name), level="success"
    )
    press_enter_to_continue(t("press_enter", new_lang))

    return new_lang
