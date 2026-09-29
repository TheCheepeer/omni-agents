#!/usr/bin/env python3
"""
Target selection and global configuration menu for omni-agents TUI.
Rendered using modern selection cards and status indicators.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.env_paths import is_default_or_system_path
from omni_agents.i18n import t
from omni_agents.targets import get_all_targets, save_workspace_state
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved
from omni_agents.tui.theme import (
    get_styled_choice,
    press_enter_to_continue,
    render_banner,
    render_selection_card,
)


def handle_target_selection(
    target_path: Path | None,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
    app_config: dict[str, Any] | None = None,
    omni_docs_dir: Path | None = None,
    is_first_run: bool = False,
) -> list[str]:
    """Interactive menu to select and toggle target tools to configure."""
    all_targets = get_all_targets()
    active_set = set(current_state.get("active_targets", []))
    if not active_set and app_config and app_config.get("active_targets"):
        active_set = set(app_config.get("active_targets", []))
    initial_set = set(active_set)

    target_items = [
        {
            "id": target.target_id,
            "name": target.display_name,
            "description": target.get_description(lang),
        }
        for target in all_targets
    ]

    title = (
        t("first_run_target_title", lang)
        if is_first_run
        else t("target_selection_title", lang)
    )
    if is_first_run:
        subtitle = t("first_run_target_subtitle", lang)
        instructions = (
            f"{t('first_run_welcome', lang)}\n\n{t('target_commands', lang)}"
        )
    else:
        subtitle = (
            f"{t('target_workspace', lang)}: {target_path}" if target_path else None
        )
        instructions = t("target_commands", lang)

    while True:
        clear_screen()
        render_selection_card(
            title=title,
            items=target_items,
            instructions=instructions,
            selected_ids=active_set,
            id_key="id",
            name_key="name",
            desc_key="description",
            footer_hint=t("hint_toggle_save_return", lang),
            subtitle=subtitle,
        )

        choice = get_styled_choice(t("your_choice", lang))

        if choice in ("v", "voltar", "volver", "q"):
            if active_set != initial_set and not confirm_exit_unsaved(lang=lang):
                continue
            break

        if choice in ("s", "salvar", "save", "guardar"):
            new_active_list = [
                target.target_id
                for target in all_targets
                if target.target_id in active_set
            ]
            if not new_active_list:
                render_banner(t("must_select_one_tool", lang), level="warning")
                press_enter_to_continue(t("press_enter", lang))
                continue

            current_state["active_targets"] = new_active_list
            if app_config is not None:
                app_config["active_targets"] = new_active_list
                app_config["tools_configured"] = True
                save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)

            if (
                target_path
                and target_path.exists()
                and target_path.is_dir()
                and not is_default_or_system_path(target_path)
            ):
                save_workspace_state(target_path, current_state)
                apply_workspace_to_targets(
                    target_path=target_path,
                    repo_root=repo_root,
                    scanned=scanned,
                    active_target_ids=new_active_list,
                    selected_agent_ids=current_state.get("selected_agents", []),
                    selected_rule_ids=current_state.get("selected_rules", []),
                    selected_skills_dict=current_state.get("selected_skills", {}),
                    lang=lang,
                )
            render_banner(t("targets_updated", lang), level="success")
            press_enter_to_continue(t("press_enter", lang))
            return new_active_list

        if choice == "":
            continue

        if choice == "all":
            active_set = {target.target_id for target in all_targets}
        elif choice in ("limpar", "clear", "limpiar"):
            active_set.clear()
        else:
            tokens = [
                token.strip()
                for token in choice.replace(";", ",").split(",")
                if token.strip()
            ]
            for token in tokens:
                if token.isdigit():
                    num = int(token)
                    if 1 <= num <= len(all_targets):
                        tid = all_targets[num - 1].target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)
                else:
                    matched = next(
                        (target for target in all_targets if target.target_id == token),
                        None,
                    )
                    if matched:
                        tid = matched.target_id
                        if tid in active_set:
                            active_set.remove(tid)
                        else:
                            active_set.add(tid)

    return list(active_set)


def handle_global_configuration(
    repo_root: Path,
    scanned: dict[str, Any],
    app_config: dict[str, Any],
    omni_docs_dir: Path | None = None,
    lang: str = "en",
) -> None:
    """Menu for managing global machine-wide configuration links (Antigravity, Claude, etc.)."""
    targets_with_global = [
        target for target in get_all_targets() if target.supports_global
    ]
    global_items = [
        {
            "id": target.target_id,
            "name": target.display_name,
            "description": target.get_description(lang),
        }
        for target in targets_with_global
    ]

    clear_screen()
    render_selection_card(
        title=t("global_title", lang),
        items=global_items,
        instructions=t("global_options", lang),
        selected_ids=set(),
        id_key="id",
        name_key="name",
        desc_key="description",
        footer_hint=t("hint_link_global", lang),
        subtitle=t("global_subtitle", lang),
    )

    choice = get_styled_choice(t("your_choice", lang))

    if choice in ("v", "voltar", "volver", "q", ""):
        return

    rules = scanned.get("rules", [])
    rules_map = {r["id"]: r for r in rules}
    global_rule_ids = app_config.get("global_rules", [])
    configured_rules = [rules_map[rid] for rid in global_rule_ids if rid in rules_map]

    if choice == "all":
        for target in targets_with_global:
            render_banner(t("linking", lang, tool=target.display_name), level="info")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
        render_banner(t("global_rules_info_note", lang), level="success")
        press_enter_to_continue(t("press_enter", lang))
        return

    if choice in ("limpar", "clear", "limpiar"):
        render_banner(t("cleaning_global", lang), level="warning")
        for target in targets_with_global:
            target.clean_global(lang=lang)
        app_config["global_rules"] = []
        save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
        press_enter_to_continue(t("press_enter", lang))
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(targets_with_global):
            target = targets_with_global[num - 1]
            render_banner(t("linking", lang, tool=target.display_name), level="info")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
            render_banner(t("global_rules_info_note", lang), level="success")
            press_enter_to_continue(t("press_enter", lang))
