#!/usr/bin/env python3
"""
Interactive workspace clean menu for omni-agents TUI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from omni_agents.i18n import t
from omni_agents.targets import get_all_targets, save_workspace_state
from omni_agents.tui.common import clear_screen


def handle_clean_workspace(
    target_path: Path,
    current_state: dict[str, Any],
    lang: str = "en",
) -> None:
    """Option: Cleanup and uninstallation isolated by target tool."""
    clear_screen()
    print("\n" + "=" * 65)
    print(f"  {t('clean_title', lang)}")
    print("=" * 65)
    print(f"{t('target_workspace', lang)}: {target_path}\n")

    all_targets = get_all_targets()
    active_targets = current_state.get("active_targets", [])

    print(t("configured_tools", lang))
    for idx, target in enumerate(all_targets, 1):
        status = "(Active)" if target.target_id in active_targets else "(Inactive)"
        print(f"  [{idx}] {target.display_name:<26} {status}")

    print("\n" + "-" * 65)
    print(t("clean_options", lang))
    print("-" * 65)

    try:
        choice = input(f"\n{t('your_choice', lang)}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if choice in ("v", "voltar", "volver", ""):
        return

    if choice == "all":
        for target in all_targets:
            target.clean_workspace(target_path, lang=lang)
        current_state["active_targets"] = []
        save_workspace_state(target_path, current_state)
        print(f"\n[OK] {t('clean_all_done', lang)}")
        try:
            input(f"\n{t('press_enter', lang)}")
        except (EOFError, KeyboardInterrupt):
            pass
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
            print(f"\n[OK] {t('clean_target_done', lang, target=target.display_name)}")
            try:
                input(f"\n{t('press_enter', lang)}")
            except (EOFError, KeyboardInterrupt):
                pass
