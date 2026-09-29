#!/usr/bin/env python3
"""
Target selection and global configuration menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.core.config import save_app_config
from omni_agents.core.linker import apply_workspace_to_targets
from omni_agents.i18n import t
from omni_agents.targets import get_all_targets
from omni_agents.tui.common import clear_screen, confirm_exit_unsaved


def handle_target_selection(
    target_path: Path,
    repo_root: Path,
    scanned: dict[str, Any],
    current_state: dict[str, Any],
    lang: str = "en",
) -> list[str]:
    """Interactive menu to select and toggle target tools to configure."""
    all_targets = get_all_targets()
    active_set = set(current_state.get("active_targets", []))
    if not active_set:
        active_set.add("antigravity")
    initial_set = set(active_set)

    while True:
        clear_screen()
        print("\n" + "=" * 65)
        print(f"  {t('target_selection_title', lang)}")
        print("=" * 65)
        print(f"{t('target_workspace', lang)}: {target_path}\n")
        print(f"{t('target_available', lang)}")

        for idx, target in enumerate(all_targets, 1):
            is_active = "[x]" if target.target_id in active_set else "[ ]"
            print(
                f"  [{idx}] {is_active} {target.display_name:<26} - {target.get_description(lang)}"
            )

        print("\n" + "-" * 65)
        print(t("target_commands", lang))
        print("-" * 65)

        try:
            choice = input(f"\n{t('your_choice', lang)}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if choice in ("v", "voltar", "volver"):
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
                print(f"  [!] {t('must_select_one_tool', lang)}")
                try:
                    input(t("press_enter", lang))
                except (EOFError, KeyboardInterrupt):
                    pass
                continue

            current_state["active_targets"] = new_active_list
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
            print(f"\n[OK] {t('targets_updated', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
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
    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('global_title', lang)}")
    print("=" * 65)
    print(t("global_subtitle", lang))

    targets_with_global = [
        target for target in get_all_targets() if target.supports_global
    ]
    for idx, target in enumerate(targets_with_global, 1):
        print(f"  [{idx}] {target.display_name:<26} - {target.get_description(lang)}")

    print("\n" + "-" * 65)
    print(t("global_options", lang))
    print("-" * 65)

    try:
        choice = input(f"\n{t('your_choice', lang)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", "volver", ""):
        return

    rules = scanned.get("rules", [])
    rules_map = {r["id"]: r for r in rules}
    global_rule_ids = app_config.get("global_rules", [])
    configured_rules = [rules_map[rid] for rid in global_rule_ids if rid in rules_map]

    if choice == "all":
        for target in targets_with_global:
            print(f"\n-> {t('linking', lang, tool=target.display_name)}")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
        print(f"\n[i] {t('global_rules_info_note', lang)}")
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice in ("limpar", "clear", "limpiar"):
        print(f"\n-> {t('cleaning_global', lang)}")
        for target in targets_with_global:
            target.clean_global(lang=lang)
        app_config["global_rules"] = []
        save_app_config(repo_root, app_config, omni_docs_dir=omni_docs_dir)
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
        return

    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(targets_with_global):
            target = targets_with_global[num - 1]
            print(f"\n-> {t('linking', lang, tool=target.display_name)}")
            target.configure_global(
                repo_root,
                lang=lang,
                selected_rules=configured_rules,
            )
            print(f"\n[i] {t('global_rules_info_note', lang)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
