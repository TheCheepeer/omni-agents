#!/usr/bin/env python3
"""
Interactive workspace clean menu for omni-agents TUI.
Rendered using styled danger cards and status indicators.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.targets import get_all_targets, save_workspace_state
from omni_agents.tui.common import clear_screen
from omni_agents.tui.theme import (
    COLOR_DANGER,
    COLOR_MUTED,
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


def handle_clean_workspace(
    target_path: Path,
    current_state: dict[str, Any],
    lang: str = "en",
) -> None:
    """Option: Cleanup and uninstallation isolated by target tool."""
    clear_screen()

    all_targets = get_all_targets()
    active_targets = current_state.get("active_targets", [])

    table = Table(box=None, show_header=False, padding=(0, 1), expand=True)
    table.add_column(t("table_col_index", lang), style="dim", width=6, justify="right")
    table.add_column(t("table_col_name", lang), style="bold white", width=26)
    table.add_column(t("table_col_status", lang), width=16)

    for idx, target in enumerate(all_targets, 1):
        is_active = target.target_id in active_targets
        status_markup = (
            f"[bold {COLOR_SUCCESS}]● {t('status_active', lang)}[/bold {COLOR_SUCCESS}]"
            if is_active
            else f"[{COLOR_MUTED}]○ {t('status_inactive', lang)}[/{COLOR_MUTED}]"
        )
        table.add_row(escape(f"[{idx:2d}]"), escape(target.display_name), status_markup)

    panel = Panel(
        table,
        title=f"[bold {COLOR_DANGER}]{escape(t('clean_title', lang))}[/bold {COLOR_DANGER}]",
        title_align="left",
        subtitle=f"[{COLOR_MUTED}]{escape(str(target_path))}[/{COLOR_MUTED}]",
        subtitle_align="right",
        box=box.ROUNDED,
        border_style="dim red",
        padding=(1, 1),
    )
    console.print(panel)

    instructions_panel = Panel(
        f"[{COLOR_MUTED}]{escape(t('clean_options', lang))}[/{COLOR_MUTED}]",
        box=box.ROUNDED,
        border_style="dim",
        padding=(0, 1),
    )
    console.print(instructions_panel)

    choice = get_styled_choice(t("your_choice", lang))

    if choice in ("v", "voltar", "volver", "q", ""):
        return

    if choice == "all":
        for target in all_targets:
            target.clean_workspace(target_path, lang=lang)
        current_state["active_targets"] = []
        save_workspace_state(target_path, current_state)
        render_banner(t("clean_all_done", lang), level="success")
        press_enter_to_continue(t("press_enter", lang))
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(all_targets):
            target = all_targets[num - 1]
            target.clean_workspace(target_path, lang=lang)
            if target.target_id in active_targets:
                active_targets.remove(target.target_id)
                current_state["active_targets"] = active_targets
                save_workspace_state(target_path, current_state)
            render_banner(
                t("clean_target_done", lang, target=target.display_name),
                level="success",
            )
            press_enter_to_continue(t("press_enter", lang))
