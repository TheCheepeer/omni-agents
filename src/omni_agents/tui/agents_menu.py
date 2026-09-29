#!/usr/bin/env python3
"""
Agents selection and activation menu for omni-agents TUI.
Rendered using modern selection cards and status indicators.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.i18n import t
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved
from omni_agents.tui.theme import (
    get_styled_choice,
    press_enter_to_continue,
    render_banner,
    render_selection_card,
)


def handle_agents(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    all_scanned: dict[str, Any] | None = None,
    lang: str = "en",
) -> None:
    """Option: Subagents selection and activation for target workspace."""
    agents = scanned["agents"]
    if not agents:
        render_banner(t("no_agents_found", lang), level="warning")
        press_enter_to_continue(t("press_enter_menu", lang))
        return

    curr_selected = set(current_state.get("selected_agents", []))
    initial_selected = set(curr_selected)

    while True:
        clear_screen()
        render_selection_card(
            title=t("agents_title", lang),
            items=agents,
            instructions=t("how_to_select_agents", lang),
            selected_ids=curr_selected,
            id_key="id",
            name_key="id",
            desc_key="description",
            footer_hint=t("hint_toggle_save_return", lang),
            subtitle=f"{t('target_workspace', lang)}: {target_path}",
        )

        user_input = get_styled_choice(t("your_choice", lang))

        if user_input in ("v", "voltar", "volver", "q"):
            if curr_selected != initial_selected and not confirm_exit_unsaved(
                lang=lang
            ):
                continue
            return

        if user_input in ("s", "salvar", "save", "guardar"):
            current_state["selected_agents"] = sorted(curr_selected)
            active_target_ids = current_state.get("active_targets", [])
            if not active_target_ids:
                render_banner(t("no_tools_selected_warning", lang), level="warning")
                press_enter_to_continue(t("press_enter_menu", lang))
                return

            apply_workspace_to_targets(
                target_path=target_path,
                repo_root=repo_root,
                scanned=all_scanned or scanned,
                active_target_ids=active_target_ids,
                selected_agent_ids=current_state["selected_agents"],
                selected_rule_ids=current_state.get("selected_rules", []),
                selected_skills_dict=current_state.get("selected_skills", {}),
                lang=lang,
            )
            render_banner(
                t("agents_activated", lang, count=len(curr_selected)), level="success"
            )
            press_enter_to_continue(t("press_enter_menu", lang))
            return

        if user_input == "":
            continue

        if user_input == "all":
            curr_selected = {agent["id"] for agent in agents}
            render_banner(t("all_agents_marked", lang), level="info")
        elif user_input in ("limpar", "clear", "limpiar"):
            curr_selected.clear()
            render_banner(t("all_agents_cleared", lang), level="info")
        else:
            tokens = [
                token.strip()
                for token in user_input.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(agents):
                        aid = agents[num - 1]["id"]
                        if aid in curr_selected:
                            curr_selected.remove(aid)
                        else:
                            curr_selected.add(aid)
                else:
                    matched = next(
                        (
                            a
                            for a in agents
                            if a["id"].lower() == token
                            or a["id"].lower().replace(".md", "") == token
                        ),
                        None,
                    )
                    if matched:
                        aid = matched["id"]
                        if aid in curr_selected:
                            curr_selected.remove(aid)
                        else:
                            curr_selected.add(aid)
